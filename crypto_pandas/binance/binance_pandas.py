import pandas as pd

datetime_columns = {
    "fundingTime",
    "openTime",
    "closeTime",
    "transferDate",
    "time",
    "timestamp",
    "updateTime",
    "workingTime"
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
}


def response_to_dict(data: dict) -> dict:
    for key, value in data.items():
        if key in datetime_columns:
            data[key] = pd.Timestamp(value, unit="ms")
        if key in numeric_columns:
            data[key] = float(value)
    return data


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    datetime_columns_to_convert = [x for x in df.columns if x in datetime_columns]
    df[datetime_columns_to_convert] = df[datetime_columns_to_convert].apply(
        pd.to_datetime, unit="ms"
    )
    numeric_columns_to_convert = [x for x in df.columns if x in numeric_columns]
    df[numeric_columns_to_convert] = df[numeric_columns_to_convert].apply(pd.to_numeric)
    return df


def response_to_dataframe(data: list, column_names: list = None) -> pd.DataFrame:
    df = pd.DataFrame(data)
    if column_names:
        df.columns = column_names
    return preprocess_dataframe(df)


def depth_to_dataframe(data: dict) -> pd.DataFrame:
    asks = pd.DataFrame(data=data["asks"], columns=["price", "qty"])
    bids = pd.DataFrame(data=data["asks"], columns=["price", "qty"])
    asks["side"] = "ask"
    bids["side"] = "bid"
    data = pd.concat([bids, asks], ignore_index=True)
    return preprocess_dataframe(data)


def account_to_dataframe(data: dict) -> pd.DataFrame:
    data = pd.json_normalize(
        data=data,
        meta=[
            "makerCommission",
            "takerCommission",
            "buyerCommission",
            "sellerCommission",
            ["commissionRates", "maker"],
            ["commissionRates", "taker"],
            ["commissionRates", "buyer"],
            ["commissionRates", "seller"],
            "canTrade",
            "canWithdraw",
            "canDeposit",
            "brokered",
            "requireSelfTradePrevention",
            "preventSor",
            "updateTime",
            "accountType",
            "permissions",
            "uid",
        ],
        record_path="balances",
    )
    return preprocess_dataframe(data)


def order_list_to_dataframe(data: dict) -> pd.DataFrame:
    data = pd.json_normalize(
        data=data,
        meta=[
            "orderListId",
            "contingencyType",
            "listStatusType",
            "listOrderStatus",
            "listClientOrderId",
            "transactionTime",
            "symbol",
            "isIsolated",
        ],
        record_path="orders",
    )
    return preprocess_dataframe(data)
