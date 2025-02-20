from typing import Union

import pandas as pd

from crypto_pandas.ccxt.preprocessing import (
    response_to_dataframe_ccxt,
    preprocess_dataframe_ccxt,
    expand_dict_columns,
)
from crypto_pandas.utils.pandas_utils import depth_to_dataframe


def depth_to_dataframe_ccxt(data: Union[dict, list]) -> pd.DataFrame:
    data = depth_to_dataframe(data)
    return preprocess_dataframe_ccxt(data)


ohlcv_column_names = [
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
]


def ohlcv_to_dataframe_ccxt(data: list) -> pd.DataFrame:
    return response_to_dataframe_ccxt(data, column_names=ohlcv_column_names)


def market_to_dataframe(data: dict) -> pd.DataFrame:
    data = list(data.values())
    data = pd.DataFrame(data).drop(columns=["info"])
    data = expand_dict_columns(data)
    return preprocess_dataframe_ccxt(data)


def signed_price(data: pd.DataFrame) -> pd.Series:
    return (2 * (data["side"] == "asks") - 1) * data["price"]


def sort_depth(data: pd.DataFrame, by_exchange: bool = False) -> pd.DataFrame:
    data["signed_price"] = signed_price(data)
    sort_columns = ["symbol", "side", "signed_price"]
    if by_exchange:
        sort_columns = ["exchange"] + sort_columns
    return data.sort_values(sort_columns, ignore_index=True)
