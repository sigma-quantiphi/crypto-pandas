import pandas as pd
from crypto_pandas.utils.utils import preprocess_dict
from crypto_pandas.utils.pandas_utils import preprocess_dataframe

int_datetime_columns = {
    "closeTime",
    "createDate",
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
    "amount",
    "askIV",
    "askPrice",
    "askQty",
    "available",
    "avgCostTimestampOfLast30d",
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
    "exercisePrice",
    "equity",
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
    return preprocess_dict(
        data=data,
        int_datetime_columns=int_datetime_columns,
        str_float_columns=numeric_columns,
    )


def preprocess_dataframe_binance(data: pd.DataFrame) -> pd.DataFrame:
    return preprocess_dataframe(
        data=data,
        int_datetime_columns=int_datetime_columns,
        numeric_columns=numeric_columns,
        str_bool_columns=str_bool_columns,
    )


def response_to_dataframe_binance(data: list, column_names: list = None) -> pd.DataFrame:
    data = pd.DataFrame(data=data)
    if column_names:
        data.columns = column_names
    return preprocess_dataframe_binance(data=data)
