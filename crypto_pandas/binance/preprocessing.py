import pandas as pd
from crypto_pandas.utils.pandas_utils import preprocess_dataframe

int_datetime_columns = {
    "fundingTime",
    "openTime",
    "closeTime",
    "transferDate",
    "time",
    "timestamp",
    "updateTime",
    "workingTime",
    "expiryDate",
}
date_time_to_int_keys = {
    "startTime",
    "endTime",
    "beginTime",
    "subscriptionStartTime",
}
numeric_columns = {
    "fundingRate",
    "markPrice",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quoteAssetVolume",
    "takerBuyBaseAssetVolume",
    "takerBuyQuoteAssetVolume",
    "price",
    "qty",
    "quoteQty",
    "priceChange",
    "priceChangePercent",
    "weightedAvgPrice",
    "prevClosePrice",
    "lastPrice",
    "lastQty",
    "bidPrice",
    "bidQty",
    "askPrice",
    "askQty",
    "openPrice",
    "highPrice",
    "lowPrice",
    "quoteVolume",
    "freeze",
    "withdrawing",
    "free",
    "locked",
    "markPrice",
    "bidIV",
    "askIV",
    "markIV",
    "delta",
    "theta",
    "gamma",
    "vega",
    "highPriceLimit",
    "lowPriceLimit",
    "riskFreeInterest",
    "strikePrice",
}


def preprocess_dict_binance(data: dict) -> dict:
    return preprocess_dict(data, int_datetime_columns=int_datetime_columns)


def preprocess_dataframe_binance(data: pd.DataFrame) -> pd.DataFrame:
    return preprocess_dataframe(
        data, int_datetime_columns=int_datetime_columns, numeric_columns=numeric_columns
    )


def response_to_dataframe(data: list, column_names: list = None) -> pd.DataFrame:
    data = pd.DataFrame(data)
    if column_names:
        data.columns = column_names
    return preprocess_dataframe_binance(data)
