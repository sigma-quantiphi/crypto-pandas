import pandas as pd

from crypto_pandas.bybit.preprocessing import preprocess_dataframe_bybit

market_klines_column_names = [
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "turnover",
    "category",
    "symbol",
]
market_mark_price_kline_columns = [
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "category",
    "symbol",
]


def market_kline_response_to_dataframe(data: dict) -> pd.DataFrame:
    df = pd.json_normalize(
        data=data["result"], record_path="list", meta=["category", "symbol"]
    )
    df.columns = market_klines_column_names
    return preprocess_dataframe_bybit(df)


def market_mark_price_kline_response_to_dataframe(data: dict) -> pd.DataFrame:
    df = pd.json_normalize(
        data=data["result"], record_path="list", meta=["category", "symbol"]
    )
    df.columns = market_mark_price_kline_columns
    return preprocess_dataframe_bybit(df)


def orderbook_response_to_dataframe(data: dict) -> pd.DataFrame:
    df = []
    for side in ["a", "b"]:
        df_temp = pd.json_normalize(
            data=data["result"], record_path=side, meta=["s", "ts", "u", "seq", "cts"]
        )
        df_temp["side"] = "ask" if side == "a" else "bid"
        df.append(df_temp)
    df = pd.concat(df, ignore_index=True)
    df.columns = [
        "price",
        "quantity",
        "symbol",
        "timestamp",
        "updateId",
        "sequenceId",
        "creationTimestamp",
        "side",
    ]
    return preprocess_dataframe_bybit(df)
