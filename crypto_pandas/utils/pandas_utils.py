from typing import Union

import numpy as np
import pandas as pd


def date_time_column_to_int(data: pd.Series) -> int:
    return (data.astype(int) / 1e6).astype(int)


def format_value(value: float, step_size: float = 0.001) -> str:
    """Rounds the data according to the provided step size"""
    if step_size >= 1:
        formatted_value = str(int(round(value / step_size) * step_size))
    else:
        decimals = abs(int(np.log10(step_size)))
        formatted_value = f"{value:.{decimals}f}"
    return formatted_value


def preprocess_dataframe(
    data: pd.DataFrame,
    int_datetime_columns: set = None,
    str_datetime_columns: set = None,
    numeric_columns: set = None,
    str_bool_columns: set = None,
) -> pd.DataFrame:
    if int_datetime_columns:
        datetime_columns_to_convert = [
            x for x in data.columns if x in int_datetime_columns
        ]
        data[datetime_columns_to_convert] = (
            data[datetime_columns_to_convert]
            .apply(pd.to_numeric)
            .apply(pd.to_datetime, unit="ms")
            .apply(lambda x: x.dt.tz_localize("UTC"))
        )
    if str_datetime_columns:
        datetime_columns_to_convert = [
            x for x in data.columns if x in str_datetime_columns
        ]
        data[datetime_columns_to_convert] = (
            data[datetime_columns_to_convert]
            .apply(pd.to_datetime)
            .apply(lambda x: x.dt.tz_localize("UTC"))
        )
    if numeric_columns:
        numeric_columns_to_convert = [x for x in data.columns if x in numeric_columns]
        data[numeric_columns_to_convert] = data[numeric_columns_to_convert].apply(
            pd.to_numeric
        )
    if str_bool_columns:
        bool_columns_to_convert = [x for x in data.columns if x in str_bool_columns]
        data[bool_columns_to_convert] = data[bool_columns_to_convert].astype(bool)
    return data


possible_depth_meta = ["symbol", "timestamp", "datetime", "nonce", "exchange", "T", "u"]


def depth_to_dataframe(data: Union[dict, list]) -> pd.DataFrame:
    dfs = []
    if isinstance(data, list):
        keys = data[0].keys()
    else:
        keys = data.keys()
    meta = [x for x in keys if x in possible_depth_meta]
    for x in ["asks", "bids"]:
        df = pd.json_normalize(
            data=data,
            record_path=x,
            meta=meta,
        )
        df["side"] = x
        dfs.append(df)
    if dfs:
        data = pd.concat(dfs, ignore_index=True).rename(
            columns={0: "price", 1: "qty", "T": "timestamp", "u": "updateId"}
        )
        return data


def create_buy_and_sell_orders(
    orders: pd.DataFrame, sides: tuple = ("BUY", "SELL")
) -> pd.DataFrame:
    dfs = []
    data = orders.copy()
    for side in sides:
        data["side"] = side
        dfs.append(data.copy())
    return pd.concat(dfs)


def floor_series(data: pd.Series, digits: int = 0) -> pd.Series:
    return np.floor(data * 10**digits) / 10**digits


def ceil_series(data: pd.Series, digits: int = 0) -> pd.Series:
    return np.ceil(data * 10**digits) / 10**digits
