import pandas as pd
from typing import Union
from crypto_pandas.binance.preprocessing import (
    response_to_dataframe,
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


def klines_to_dataframe(data: list) -> pd.DataFrame:
    return response_to_dataframe(data, column_names=klines_column_names)


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
        return preprocess_dataframe_binance(data)
