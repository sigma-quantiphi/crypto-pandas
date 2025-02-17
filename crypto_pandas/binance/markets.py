import pandas as pd
from typing import Union
from crypto_pandas.binance.preprocessing import (
    response_to_dataframe_binance,
    preprocess_dataframe_binance,
)

klines_column_names = [
    "openTime",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "closeTime",
    "quoteAssetVolume",
    "numberOfTrades",
    "takerBuyBaseAssetVolume",
    "takerBuyQuoteAssetVolume",
    "ignore",
]
agg_trades_columns = [
    "tradeId",
    "price",
    "qty",
    "firstTradeId",
    "lastTradeId",
    "timestamp",
    "isBuyerMaker",
    "ignore",
]
possible_depth_meta = ["symbol", "timestamp", "datetime", "nonce", "exchange", "T", "u"]


def exchange_info_to_dataframe(
    data: list, record_path: str = "symbols"
) -> pd.DataFrame:
    meta = ["timezone", "serverTime", "rateLimits"]
    if record_path == "symbols":
        meta.append("exchangeFilters")
    data = pd.json_normalize(
        data=data,
        record_path=record_path,
        meta=meta,
    )
    data.columns = [x.replace(f"{record_path}.", "") for x in data.columns]
    return preprocess_dataframe_binance(data=data)


def klines_to_dataframe(data: list) -> pd.DataFrame:
    return response_to_dataframe_binance(data, column_names=klines_column_names)


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
        return preprocess_dataframe_binance(data)
