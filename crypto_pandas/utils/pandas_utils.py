import numpy as np
import pandas as pd
import pandera as pa

order_data_columns = [
    "symbol",
    "precision_amount",
    "precision_price",
    "limits_price.min",
    "limits_price.max",
    "limits_amount.min",
    "limits_amount.max",
]


def format_timestamp(timestamp: int | pd.Timestamp | dict | str | None) -> pd.Timestamp:
    now = pd.Timestamp.now(tz="UTC")
    if isinstance(timestamp, dict):
        timestamp = now + pd.DateOffset(**timestamp)
    elif isinstance(timestamp, str):
        timestamp = now + pd.Timedelta(timestamp)
    return timestamp


def timestamp_to_int(timestamp: int | pd.Timestamp | dict | str | None) -> int:
    timestamp = format_timestamp(timestamp)
    if isinstance(timestamp, pd.Timestamp):
        timestamp = int(timestamp.timestamp() * 1000)
    return timestamp


def date_time_fields_to_int_str(data: dict) -> dict:
    def transform_value(value):
        if isinstance(value, pd.Timestamp):
            return str(int(value.timestamp() * 1000))
        elif isinstance(value, dict):
            return date_time_fields_to_int_str(value)
        elif isinstance(value, list):
            return [transform_value(v) for v in value]
        return value

    return {key: transform_value(value) for key, value in data.items()}


def date_time_columns_to_int_str(data: pd.DataFrame) -> pd.DataFrame:
    columns = (
        data.select_dtypes("datetimetz").columns.tolist()
        + data.select_dtypes("datetime").columns.tolist()
    )
    data[columns] = (data[columns].astype("int64") // 10**6).astype(str)
    return data


def expand_dict_columns(data: pd.DataFrame, separator: str = ".") -> pd.DataFrame:
    data = data.reset_index(drop=True)
    dict_columns = [
        x for x in data.columns if all(data[x].apply(lambda y: isinstance(y, dict)))
    ]
    columns_list = [data.drop(columns=dict_columns).copy()]
    for dict_column in dict_columns:
        exploded_column = pd.json_normalize(data[dict_column])
        exploded_column.columns = [
            f"{dict_column}{separator}{x}" for x in exploded_column.columns
        ]
        columns_list.append(exploded_column.copy())
    return pd.concat(columns_list, axis=1)


def determine_mandatory_optional_fields_pandera(model: pa.DataFrameModel) -> dict:
    schema = model.to_schema()
    fields = {"mandatory": [], "optional": []}
    for col_name, col_obj in schema.columns.items():
        if col_obj.nullable:
            fields["optional"].append(col_name)
        else:
            fields["mandatory"].append(col_name)
    return fields


def combine_params(row: pd.Series, param_cols: list) -> dict:
    return {
        column.replace("params.", ""): row[column]
        for column in param_cols
        if pd.notnull(row[column])
    }


def round_price(price: float, precision: float, side: str, strategy: str) -> float:
    price /= precision
    if (
        strategy == "defensive"
        and side == "buy"
        or strategy == "aggressive"
        and side == "sell"
    ):
        price = np.floor(price)
    elif (
        strategy == "defensive"
        and side == "sell"
        or strategy == "aggressive"
        and side == "buy"
    ):
        price = np.ceil(price)
    else:
        price = round(price)
    return price * precision


def round_amount(amount: float, precision: float, strategy: str) -> float:
    amount /= precision
    if strategy == "floor":
        amount = np.floor(amount)
    elif strategy == "ceil":
        amount = np.ceil(amount)
    else:
        amount = round(amount)
    return amount * precision


def preprocess_order(
    symbol: str,
    type: str,
    side: str,
    amount: float,
    price: float,
    notional: float,
    markets: pd.DataFrame,
    max_notional: float,
    price_strategy: str,
    amount_strategy: str,
) -> tuple:

    market = markets.query(f"symbol == '{symbol}'").to_dict("records")[0]
    if type == "limit":
        if pd.isnull(price):
            raise ValueError("Missing price for limit order.")
        if pd.notnull(notional):
            amount = notional / price
        elif pd.notnull(amount):
            notional = amount * price
        else:
            raise ValueError("Either notional or amount is required for limit order.")
        if notional > max_notional:
            raise ValueError(
                f"Order notional {notional} larger than limit {max_notional}"
            )
        price = round_price(
            price=price,
            precision=market["precision_price"],
            side=side,
            strategy=price_strategy,
        )
        if pd.notnull(market["limits_price.min"]) and pd.notnull(
            market["limits_price.max"]
        ):
            price = np.clip(
                price, market["limits_price.min"], market["limits_price.max"]
            )
    amount = round_amount(
        amount=amount, precision=market["precision_amount"], strategy=amount_strategy
    )
    if pd.notnull(market["limits_amount.min"]) and pd.notnull(
        market["limits_amount.max"]
    ):
        amount = np.clip(
            amount, market["limits_amount.min"], market["limits_amount.max"]
        )
    return amount, price


def check_orders_dataframe_size(
    orders: pd.DataFrame, max_number_of_orders: int = 5
) -> None:
    n_orders = len(orders.index)
    if n_orders > max_number_of_orders:
        raise ValueError(
            f"Number of orders {n_orders} larger than limit {max_number_of_orders}"
        )


def preprocess_order_dataframe(
    orders: pd.DataFrame,
    markets: pd.DataFrame,
    max_orders: int,
    max_notional: float,
    price_strategy: str,
    amount_strategy: str,
) -> pd.DataFrame:
    check_orders_dataframe_size(orders=orders, max_number_of_orders=max_orders)
    orders = date_time_columns_to_int_str(orders)
    if {"amount", "price"}.issubset(orders.columns):
        orders["notional"] = orders["amount"] * orders["price"]
    elif {"notional", "price"}.issubset(orders.columns):
        orders["amount"] = orders["notional"] / orders["price"]
    if "notional" in orders.columns:
        orders_error = orders.query(f"notional > {max_notional}")
        if not orders_error.empty:
            raise ValueError(f"Orders exceeding max notional: {orders_error}")
    orders = orders.merge(markets[order_data_columns])
    if "price" in orders.columns and orders["precision_price"].notnull().all():
        orders["price"] = orders.apply(
            lambda row: round_price(
                price=row["price"],
                precision=row["precision_price"],
                side=row["side"],
                strategy=price_strategy,
            ),
            axis=1,
        )
        orders["price"] = orders["price"].clip(
            orders["limits_price.min"], orders["limits_price.max"]
        )
    if orders["precision_amount"].notnull().all():
        orders["amount"] = orders.apply(
            lambda row: round_amount(
                amount=row["amount"],
                precision=row["precision_amount"],
                strategy=amount_strategy,
            ),
            axis=1,
        )
        orders["amount"] = orders["amount"].clip(
            orders["limits_amount.min"], orders["limits_amount.max"]
        )
    if "params" not in orders.columns:
        param_cols = orders.columns[orders.columns.str.startswith("params.")]
        orders["params"] = orders.apply(combine_params, axis=1, param_cols=param_cols)
    return orders
