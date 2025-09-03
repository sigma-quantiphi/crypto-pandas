import asyncio
import warnings
from typing import Literal, Awaitable, Any, overload

import ccxt
import numpy as np
import pandas as pd
import pandera as pa
from pandas import DataFrame

cap_zero_columns = ["limits_price.min", "limits_cost.min", "limits_amount.min"]
cap_inf_columns = ["limits_price.max", "limits_cost.max", "limits_amount.max"]
order_data_columns = ["symbol"] + cap_zero_columns + cap_inf_columns


@overload
def format_timestamp(timestamp: None) -> None: ...


@overload
def format_timestamp(timestamp: int | pd.Timestamp | dict | str) -> pd.Timestamp: ...


def format_timestamp(
    timestamp: int | pd.Timestamp | dict | str | None,
) -> pd.Timestamp | None:
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
    cost: float,
    markets: pd.DataFrame,
    max_cost: float,
    cost_out_of_range: Literal["warn", "clip"] = "warn",
    price_out_of_range: Literal["warn", "clip"] = "warn",
    amount_out_of_range: Literal["warn", "clip"] = "warn",
) -> tuple:
    market = markets.query(f"symbol == '{symbol}'").reindex(columns=order_data_columns)
    market[cap_zero_columns] = market[cap_zero_columns].fillna(0)
    market[cap_inf_columns] = market[cap_inf_columns].fillna(np.inf)
    market = market.to_dict("records")[0]
    if pd.isnull(amount):
        if pd.notnull(cost) & pd.notnull(price):
            amount = cost / price
    if order_type == "limit":
        if pd.isnull(price):
            raise ValueError("Missing price for limit order.")
        elif pd.notnull(amount):
            cost = amount * price
        else:
            raise ValueError("Either cost or amount is required for limit order.")
        if cost > max_cost:
            raise ValueError(f"Order cost {cost} larger than limit {max_cost}")
    values = {"amount": amount, "price": price, "cost": cost}
    new_values = {}
    for key, value in values.items():
        if key == "price":
            out_of_range = price_out_of_range
        elif key == "cost":
            out_of_range = cost_out_of_range
        else:
            out_of_range = amount_out_of_range
        limits_min = market[f"limits_{key}.min"]
        limits_max = market[f"limits_{key}.max"]
        if out_of_range == "warn":
            if not limits_min <= value <= limits_max:
                warnings.warn(
                    f"{key} {amount} outside limits {limits_min}, {limits_max}."
                )
                value = None
        else:
            value = np.clip(value, limits_min, limits_max)
        new_values[key] = value
    new_values["amount"] = exchange.amount_to_precision(
        symbol=symbol, amount=new_values["amount"]
    )
    new_values["price"] = exchange.price_to_precision(
        symbol=symbol, price=new_values["price"]
    )
    return new_values["amount"], new_values["price"]


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
    max_cost: float,
    cost_out_of_range: Literal["warn", "clip"] = "warn",
    price_out_of_range: Literal["warn", "clip"] = "warn",
    amount_out_of_range: Literal["warn", "clip"] = "warn",
) -> pd.DataFrame:
    check_orders_dataframe_size(orders=orders, max_number_of_orders=max_orders)
    orders = date_time_columns_to_int_str(orders)
    if {"amount", "price"}.issubset(orders.columns):
        orders["cost"] = orders["amount"] * orders["price"]
    elif {"cost", "price"}.issubset(orders.columns):
        orders["amount"] = orders["cost"] / orders["price"]
    if "cost" in orders.columns:
        orders_error = orders.query(f"cost > {max_cost}")
        if not orders_error.empty:
            raise ValueError(f"Orders exceeding max cost: {orders_error}")
    order_markets = markets.reindex(columns=order_data_columns)
    order_markets[cap_zero_columns] = order_markets[cap_zero_columns].fillna(0)
    order_markets[cap_inf_columns] = order_markets[cap_inf_columns].fillna(np.inf)
    orders = orders.merge(order_markets)
    for column, out_of_range in [
        ("cost", cost_out_of_range),
        ("price", price_out_of_range),
        ("amount", amount_out_of_range),
    ]:
        min_limit, max_limit = f"limits_{column}.min", f"limits_{column}.max"
        if column in orders.columns:
            if out_of_range == "warn":
                in_bounds = orders[column].between(orders[min_limit], orders[max_limit])
                out_of_bounds_orders = orders.loc[~in_bounds].reset_index(drop=True)
                orders = orders.loc[in_bounds].reset_index(drop=True)
                if not out_of_bounds_orders.empty:
                    warnings.warn(
                        f"Removing orders with {column} outside limits:\n{out_of_bounds_orders.to_markdown(index=False)}"
                    )
            else:
                orders[column] = orders[column].clip(
                    orders[min_limit], orders[max_limit]
                )
    if "params" not in orders.columns:
        param_cols = orders.columns[orders.columns.str.startswith("params.")]
        orders["params"] = orders.apply(combine_params, axis=1, param_cols=param_cols)
    return orders


@overload
def concat_results(
    results: list[pd.DataFrame],
    errors: Literal["raise", "warn", "ignore"] = "raise",
) -> DataFrame: ...


@overload
def concat_results(
    results: list[dict],
    errors: Literal["raise", "warn", "ignore"] = "raise",
) -> DataFrame: ...


@overload
def concat_results(
    results: list[None],
    errors: Literal["raise", "warn", "ignore"] = "raise",
) -> list[None]: ...


def concat_results(
    results: list[pd.DataFrame | dict | None],
    errors: Literal["raise", "warn", "ignore"] = "raise",
) -> DataFrame | list[dict | DataFrame | None]:
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
            return clean_results
    else:
        return pd.DataFrame()


async def async_concat_results(
    tasks: Awaitable | list[Awaitable] | list[list[Awaitable]],
    errors: Literal["raise", "warn", "ignore"] = "raise",
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
