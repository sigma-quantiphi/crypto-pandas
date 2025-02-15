import pandas as pd
from crypto_pandas.utils.utils import preprocess_dict
from crypto_pandas.utils.pandas_utils import preprocess_dataframe

int_datetime_columns = {
    "closeTime",
    "createTime",
    "deliveryDate",
    "expirationTimestamp",
    "expiryDate",
    "fundingTime",
    "nextFundingTime",
    "openTime",
    "serverTime",
    "time",
    "timestamp",
    "transferDate",
    "updateTime",
    "workingTime",
}
date_time_to_int_keys = {
    "beginTime",
    "endTime",
    "startTime",
    "subscriptionStartTime",
}
numeric_columns = {
    "askIV",
    "askPrice",
    "askQty",
    "avgPrice",
    "bidIV",
    "bidPrice",
    "bidQty",
    "breakEvenPrice",
    "close",
    "delta",
    "entryPrice",
    "estimatedSettlePrice",
    "executedQty",
    "free",
    "freeze",
    "fundingRate",
    "gamma",
    "high",
    "highPrice",
    "highPriceLimit",
    "indexPrice",
    "interestRate",
    "isolatedMargin",
    "lastFundingRate",
    "lastPrice",
    "lastQty",
    "leverage",
    "locked",
    "low",
    "lowPrice",
    "lowPriceLimit",
    "markIV",
    "markPrice",
    "markValue",
    "maxQty",
    "notionalValue",
    "open",
    "openPrice",
    "positionAmt",
    "positionCost",
    "prevClosePrice",
    "price",
    "priceChange",
    "priceChangePercent",
    "qty",
    "quantity",
    "quoteAssetVolume",
    "quoteQty",
    "quoteVolume",
    "realStrikePrice",
    "reducibleQty",
    "riskFreeInterest",
    "ror",
    "strikePrice",
    "sumOpenInterest",
    "sumOpenInterestUsd",
    "takerBuyBaseAssetVolume",
    "takerBuyQuoteAssetVolume",
    "theta",
    "unRealizedProfit",
    "unrealizedPNL",
    "vega",
    "volume",
    "weightedAvgPrice",
    "withdrawing",
}
str_bool_columns = {
    "isAutoAddMargin",
}


def preprocess_dict_binance(data: dict) -> dict:
    return preprocess_dict(data, int_datetime_columns=int_datetime_columns)


def preprocess_dataframe_binance(data: pd.DataFrame) -> pd.DataFrame:
    return preprocess_dataframe(
        data=data,
        int_datetime_columns=int_datetime_columns,
        numeric_columns=numeric_columns,
        str_bool_columns=str_bool_columns,
    )


def response_to_dataframe(data: list, column_names: list = None) -> pd.DataFrame:
    data = pd.DataFrame(data)
    if column_names:
        data.columns = column_names
    return preprocess_dataframe_binance(data)


def exchange_info_to_dataframe(
    data: list, record_path: str = "symbols"
) -> pd.DataFrame:
    meta = ["timezone", "serverTime", "rateLimits"]
    if record_path == "symbols":
        meta.append("exchangeFilters")
    df = pd.json_normalize(
        data=data,
        record_path=record_path,
        meta=meta,
    )
    df.columns = [x.replace(f"{record_path}.", "") for x in df.columns]
    return preprocess_dataframe_binance(df)
