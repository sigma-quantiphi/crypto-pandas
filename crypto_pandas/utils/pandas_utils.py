import asyncio
import warnings
from typing import Literal, Awaitable, Any

import ccxt
import numpy as np
import pandas as pd
import pandera as pa
from pandas import DataFrame

order_data_columns = [
    "symbol",
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
        x for x in data.columns if any(data[x].apply(lambda y: isinstance(y, dict)))
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


def preprocess_order(
    exchange: ccxt.Exchange,
    symbol: str,
    order_type: str,
    amount: float,
    price: float,
    notional: float,
    markets: pd.DataFrame,
    max_notional: float,
    price_out_of_range: Literal["warn", "clip"] = "warn",
    amount_out_of_range: Literal["warn", "clip"] = "warn",
) -> tuple:
    market = (
        markets.reindex(columns=order_data_columns)
        .query(f"symbol == '{symbol}'")
        .to_dict("records")[0]
    )
    if pd.isnull(amount):
        if pd.notnull(notional) & pd.notnull(price):
            amount = notional / price
    if order_type == "limit":
        if pd.isnull(price):
            raise ValueError("Missing price for limit order.")
        elif pd.notnull(amount):
            notional = amount * price
        else:
            raise ValueError("Either notional or amount is required for limit order.")
        if notional > max_notional:
            raise ValueError(
                f"Order notional {notional} larger than limit {max_notional}"
            )
        if pd.notnull(market["limits_price.min"]) and pd.notnull(
            market["limits_price.max"]
        ):
            if price_out_of_range == "warn":
                if (
                    not market["limits_price.min"]
                    <= price
                    <= market["limits_price.max"]
                ):
                    warnings.warn(
                        f"Price amount {amount} outside limits {market['limits_price.min']}, {market['limits_price.max']}."
                    )
                    price = None
            else:
                price = np.clip(
                    price, market["limits_price.min"], market["limits_price.max"]
                )
    if pd.notnull(market["limits_amount.min"]) and pd.notnull(
        market["limits_amount.max"]
    ):
        if amount_out_of_range == "warn":
            if not market["limits_amount.min"] <= amount <= market["limits_amount.max"]:
                warnings.warn(
                    f"Order amount {amount} outside limits {market['limits_amount.min']}, {market['limits_amount.max']}."
                )
                amount = None
        else:
            amount = np.clip(
                amount, market["limits_amount.min"], market["limits_amount.max"]
            )
    amount = exchange.amount_to_precision(symbol=symbol, amount=amount)
    price = exchange.price_to_precision(symbol=symbol, price=price)
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
    price_out_of_range: Literal["warn", "clip"] = "warn",
    amount_out_of_range: Literal["warn", "clip"] = "warn",
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
    orders = orders.merge(markets.reindex(columns=order_data_columns))
    if "price" in orders.columns:
        if orders[["limits_price.min", "limits_price.max"]].notnull().all(axis=1).all():
            if price_out_of_range == "warn":
                price_in_bounds = orders["price"].between(
                    orders["limits_price.min"], orders["limits_price.max"]
                )
                out_of_bounds_orders = orders.loc[~price_in_bounds].reset_index(
                    drop=True
                )
                orders = orders.loc[price_in_bounds].reset_index(drop=True)
                if not out_of_bounds_orders.empty:
                    warnings.warn(
                        f"Removing orders with price outside limits:\n{orders.to_markdown(index=False)}"
                    )
            else:
                orders["price"] = orders["price"].clip(
                    orders["limits_price.min"], orders["limits_price.max"]
                )
    if "amount" in orders.columns:
        if (
            orders[["limits_amount.min", "limits_amount.max"]]
            .notnull()
            .all(axis=1)
            .all()
        ):
            if amount_out_of_range == "warn":
                amount_in_bounds = orders["amount"].between(
                    orders["limits_amount.min"], orders["limits_amount.max"]
                )
                out_of_bounds_orders = orders.loc[~amount_in_bounds].reset_index(
                    drop=True
                )
                orders = orders.loc[amount_in_bounds].reset_index(drop=True)
                if not out_of_bounds_orders.empty:
                    warnings.warn(
                        f"Removing orders with amount outside limits:\n{orders.to_markdown(index=False)}"
                    )
            else:
                orders["amount"] = orders["amount"].clip(
                    orders["limits_amount.min"], orders["limits_amount.max"]
                )
    if "params" not in orders.columns:
        param_cols = orders.columns[orders.columns.str.startswith("params.")]
        orders["params"] = orders.apply(combine_params, axis=1, param_cols=param_cols)
    return orders


def concat_results(
    results: list[pd.DataFrame] | list[dict],
    errors: Literal["raise", "warn", "ignore"] = "raise",
) -> pd.DataFrame:
    """Concatenate results from asyncio gather"""
    clean_results, errors_results = [], []
    for x in results:
        if isinstance(x, dict):
            clean_results.append(x)
        elif isinstance(x, pd.DataFrame):
            clean_results.append(x)
        else:
            errors_results.append(x)
    if errors_results:
        if errors == "raise":
            raise ValueError(f"Errors encountered: {errors_results}")
        elif errors == "warn":
            warnings.warn(f"Errors encountered: {errors_results}")
    if clean_results:
        if all([isinstance(x, pd.DataFrame) for x in clean_results]):
            return pd.concat(clean_results, ignore_index=True)
        elif all([isinstance(x, dict) for x in clean_results]):
            return pd.DataFrame(data=clean_results).drop(
                columns=["info"], errors="ignore"
            )
        else:
            raise ValueError(
                "Results must be either a list of DataFrames or a list of dictionaries."
            )
    else:
        return pd.DataFrame()


async def async_concat_results(
    tasks: list, errors: Literal["raise", "warn", "ignore"] = "raise"
) -> DataFrame | list[DataFrame] | Any:
    # Single coroutine
    if isinstance(tasks, Awaitable):
        return await tasks
    # Flat list of awaitables
    elif all(isinstance(t, Awaitable) for t in tasks):
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return concat_results(results=results, errors=errors)
    elif all(
        isinstance(group, list) and all(isinstance(t, Awaitable) for t in group)
        for group in tasks
    ):
        flat_tasks = [t for group in tasks for t in group]
        flat_results = await asyncio.gather(*flat_tasks, return_exceptions=True)
        # Reconstruct shape
        results = []
        i = 0
        for group in tasks:
            group_size = len(group)
            group_results = flat_results[i : i + group_size]
            group_results = concat_results(results=group_results, errors=errors)
            results.append(group_results)
            i += group_size
        return results
    else:
        raise TypeError(
            "Expected coroutine, list of coroutines, or list of lists of coroutines."
        )
