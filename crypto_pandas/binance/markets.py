import pandas as pd
from typing import Union
from crypto_pandas.binance.preprocessing import (
    response_to_dataframe_binance,
    preprocess_dataframe_binance,
)
from crypto_pandas.utils.pandas_utils import depth_to_dataframe

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


def exchange_info_to_dataframe_binance(
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


def klines_to_dataframe_binance(data: list) -> pd.DataFrame:
    return response_to_dataframe_binance(data, column_names=klines_column_names)


def depth_to_dataframe_binance(data: Union[dict, list]) -> pd.DataFrame:
    data = depth_to_dataframe(data)
    return preprocess_dataframe_binance(data)
