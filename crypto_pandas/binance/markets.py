import pandas as pd

from crypto_pandas.binance.preprocessing import response_to_dataframe

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


def depth_to_dataframe(data: dict) -> pd.DataFrame:
    asks = pd.DataFrame(data=data["asks"], columns=["price", "qty"])
    bids = pd.DataFrame(data=data["bids"], columns=["price", "qty"])
    asks["side"] = "ask"
    bids["side"] = "bid"
    data = pd.concat([bids, asks], ignore_index=True)
    return preprocess_dataframe(data)
