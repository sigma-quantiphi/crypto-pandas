from functools import wraps
from typing import Callable, Literal

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


@staticmethod
def order_preprocessing(func: Callable):
    """
    A decorator for preprocessing order parameters such as price, amount, and notional
    before creating, editing, or manipulating orders.

    Args:
        func (Callable): The function to be wrapped and modified with preprocessing logic.

    Returns:
        Callable: The decorated function with added preprocessing for order parameters.
    """

    @wraps(func)
    def wrapper(
        self,
        symbol: str,
        type: Literal["limit", "market"],
        side: Literal["buy", "sell"],
        amount: float | None = None,
        price: float | None = None,
        notional: float | None = None,
        *args,
        **kwargs,
    ):
        markets = (
            self.load_markets()[order_data_columns]
            .query(f"symbol == '{symbol}'")
            .to_dict("records")[0]
        )
        if type == "limit":
            if pd.isnull(price):
                raise ValueError("Missing price for limit order.")
            else:
                if notional is not None:
                    amount = notional / price
                elif amount is not None:
                    notional = amount * price
                else:
                    raise ValueError(
                        "Either notional or amount is required for limit order."
                    )
                if notional > self.max_order_notional:
                    raise ValueError(
                        f"Order notional {notional} larger than limit {self.max_order_notional}"
                    )
                if pd.notnull(markets["precision_price"]):
                    price /= markets["precision_price"]
                    if (self.order_price_rounding == "defensive" and side == "buy") or (
                        self.order_price_rounding == "aggressive" and side == "sell"
                    ):
                        price = np.floor(price)
                    elif (
                        self.order_price_rounding == "defensive" and side == "sell"
                    ) or (self.order_price_rounding == "aggressive" and side == "buy"):
                        price = np.ceil(price)
                    else:
                        price = round(price)
                    price *= markets["precision_price"]
                if pd.notnull(markets["limits_price.min"]) and pd.notnull(
                    markets["limits_price.max"]
                ):
                    price = np.clip(
                        price,
                        markets["limits_price.min"],
                        markets["limits_price.max"],
                    )
        if pd.notnull(markets["precision_amount"]):
            amount /= markets["precision_amount"]
            if self.order_amount_rounding == "floor":
                amount = np.floor(amount)
            elif self.order_amount_rounding == "ceil":
                amount = np.ceil(amount)
            else:
                amount = round(amount)
            amount *= markets["precision_amount"]
        if pd.notnull(markets["limits_amount.min"]) and pd.notnull(
            markets["limits_amount.max"]
        ):
            amount = np.clip(
                amount,
                markets["limits_amount.min"],
                markets["limits_amount.max"],
            )
        return func(
            self,
            symbol=symbol,
            type=type,
            side=side,
            amount=amount,
            price=price,
            notional=notional,
            *args,
            **kwargs,
        )

    return wrapper


def orders_dataframe_preprocessing(self, orders: pd.DataFrame) -> list:
    """
    Preprocesses a DataFrame containing orders to validate, format, and adjust values.

    This method ensures proper formatting of datetime fields, calculates notional values
    if not present, checks for notional and order count limits, and rounds price and
    amount fields based on the rounding rules and precision constraints of the exchange.

    Args:
        orders (pd.DataFrame): A DataFrame where each row represents an order with fields
            such as 'symbol', 'amount', 'price', 'side', and optional params.

    Returns:
        list: A list of preprocessed order dictionaries, ready for API submission.

    Raises:
        ValueError: If any order exceeds the max notional value, if the number of orders
            exceeds the max allowed, or if required fields are missing during the preprocessing.
    """
    n_orders = len(orders.index)
    if n_orders > self.max_number_of_orders:
        raise ValueError(
            f"Number of orders {n_orders} larger than limit {self.max_number_of_orders}"
        )

    # Format datetime
    orders = date_time_columns_to_int_str(orders)
    if {"amount", "price"}.issubset(orders.columns):
        orders["notional"] = orders["amount"] * orders["price"]
    elif {"notional", "price"}.issubset(orders.columns):
        orders["amount"] = orders["notional"] / orders["price"]

    # Limit checks
    if "notional" in orders.columns:
        if orders.eval(f"notional > {self.max_order_notional}").any():
            errors = orders.query(f"notional > {self.max_order_notional}")
            raise ValueError(
                f"Certain orders have notional larger than max notional {self.max_number_of_orders}:\n {errors}"
            )

    markets = self.load_markets()[order_data_columns]
    orders = orders.merge(markets)
    # Round values appropriately
    if "price" in orders.columns:
        if orders["precision_price"].notnull().all():
            orders["price"] /= orders["precision_price"]
            orders["price_down"] = np.floor(orders["price"])
            orders["price_up"] = np.floor(orders["price"])
            if self.order_price_rounding == "defensive":
                orders["price"] = orders["price_down"].where(
                    orders["side"] == "buy", other=orders["price_up"]
                )
            elif self.order_price_rounding == "aggressive":
                orders["price"] = orders["price_up"].where(
                    orders["side"] == "buy", other=orders["price_down"]
                )
            else:
                orders["price"] = orders["price"].round()
            orders = orders.drop(columns=["price_down", "price_up"])
            orders["price"] *= orders["precision_price"]
        if orders[["limits_price.min", "limits_price.max"]].notnull().all().all():
            orders["price"] = orders["price"].clip(
                lower=orders["limits_price.min"],
                upper=orders["limits_price.max"],
            )
    if orders["precision_amount"].notnull().all():
        orders["amount"] /= orders["precision_amount"]
        if self.order_amount_rounding == "floor":
            orders["amount"] = np.floor(orders["amount"])
        elif self.order_amount_rounding == "ceil":
            orders["amount"] = np.ceil(orders["amount"])
        else:
            orders["amount"] = orders["amount"].round()
        orders["amount"] *= orders["precision_amount"]
    if orders[["limits_amount.min", "limits_amount.max"]].notnull().all().all():
        orders["amount"] = orders["amount"].clip(
            lower=orders["limits_amount.min"], upper=orders["limits_amount.max"]
        )
    # Serialize param columns
    if "params" not in orders.columns:
        param_cols = orders.columns[orders.columns.str.startswith("params.")]
        orders["params"] = orders.apply(combine_params, axis=1, param_cols=param_cols)
    return ccxt_processor.orders_to_dict(orders)
