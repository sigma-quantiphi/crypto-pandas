from typing import Union

import pandas as pd

from crypto_pandas.ccxt.preprocessing import (
    response_to_dataframe,
    preprocess_dataframe_ccxt,
    expand_dict_columns,
)


def depth_to_dataframe(data: Union[dict, list]) -> pd.DataFrame:
    dfs = []
    for x in ["asks", "bids"]:
        df = pd.json_normalize(
            data=data,
            record_path=x,
            meta=["symbol", "timestamp", "datetime", "nonce", "exchange"],
            errors="ignore",
        )
        df["side"] = x
        dfs.append(df)
    if dfs:
        data = pd.concat(dfs, ignore_index=True).rename(columns={0: "price", 1: "qty"})
        return preprocess_dataframe_ccxt(data)


def ohlcv_to_dataframe(data: list) -> pd.DataFrame:
    column_names = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]
    return response_to_dataframe(data, column_names=column_names)


def signed_price(data: pd.DataFrame) -> pd.Series:
    return (2 * (data["side"] == "asks") - 1) * data["price"]


def sort_depth(data: pd.DataFrame, by_exchange: bool = False) -> pd.DataFrame:
    data["signed_price"] = signed_price(data)
    sort_columns = ["symbol", "side", "signed_price"]
    if by_exchange:
        sort_columns = ["exchange"] + sort_columns
    return data.sort_values(sort_columns, ignore_index=True)


def market_to_dataframe(data: dict) -> pd.DataFrame:
    data = list(data.values())
    data = pd.DataFrame(data).drop(columns=["info"])
    data = expand_dict_columns(data)
    return preprocess_dataframe_ccxt(data)
