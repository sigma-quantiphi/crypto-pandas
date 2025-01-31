import pandas as pd

from crypto_pandas.bybit.column_names import (
    market_klines_column_names,
    market_mark_price_kline_columns,
)

datetime_columns = {"timestamp", "creationTimestamp", "fundingRateTimestamp"}
numeric_columns = {
    "equity",
    "totalMarginBalance",
    "locked",
    "totalPositionIM",
    "totalWalletBalance",
    "accountIMRate",
    "totalEquity",
    "accountMMRate",
    "bonus",
    "totalPerpUPL",
    "availableToWithdraw",
    "accruedInterest",
    "spotHedgingQty",
    "totalOrderIM",
    "totalPositionMM",
    "totalAvailableBalance",
    "collateralSwitch",
    "totalMaintenanceMargin",
    "availableToBorrow",
    "borrowAmount",
    "cumRealisedPnl",
    "accountLTV",
    "usdValue",
    "unrealisedPnl",
    "totalInitialMargin",
    "marginCollateral",
    "walletBalance",
    "price",
    "quantity",
    "updateId",
    "sequenceId",
    "lastPrice",
    "indexPrice",
    "markPrice",
    "prevPrice24h",
    "price24hPcnt",
    "highPrice24h",
    "lowPrice24h",
    "prevPrice1h",
    "openInterest",
    "openInterestValue",
    "turnover24h",
    "volume24h",
    "fundingRate",
    "nextFundingTime",
    "predictedDeliveryPrice",
    "basisRate",
    "deliveryFeeRate",
    "deliveryTime",
    "ask1Size",
    "bid1Price",
    "ask1Price",
    "bid1Size",
    "basis",
}


def preprocess_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    datetime_columns_to_convert = [x for x in data.columns if x in datetime_columns]
    data[datetime_columns_to_convert] = (
        data[datetime_columns_to_convert]
        .apply(pd.to_numeric)
        .apply(pd.to_datetime, unit="ms")
    )
    numeric_columns_to_convert = [x for x in data.columns if x in numeric_columns]
    data[numeric_columns_to_convert] = data[numeric_columns_to_convert].apply(
        pd.to_numeric
    )
    return data


def market_kline_response_to_dataframe(data: dict) -> pd.DataFrame:
    df = pd.json_normalize(
        data=data["result"], record_path="list", meta=["category", "symbol"]
    )
    df.columns = market_klines_column_names
    return preprocess_dataframe(df)


def market_mark_price_kline_response_to_dataframe(data: dict) -> pd.DataFrame:
    df = pd.json_normalize(
        data=data["result"], record_path="list", meta=["category", "symbol"]
    )
    df.columns = market_mark_price_kline_columns
    return preprocess_dataframe(df)


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
    return preprocess_dataframe(df)


def market_tickers_response_to_dataframe(data: dict) -> pd.DataFrame:
    df = pd.json_normalize(data=data["result"], record_path="list", meta=["category"])
    return preprocess_dataframe(df)


def account_wallet_balance_response_to_dataframe(data: dict) -> pd.DataFrame:
    df = pd.json_normalize(
        data=data["result"]["list"],
        record_path="coin",
        meta=[
            "totalEquity",
            "accountIMRate",
            "totalMarginBalance",
            "totalInitialMargin",
            "accountType",
            "totalAvailableBalance",
            "accountMMRate",
            "totalPerpUPL",
            "totalWalletBalance",
            "accountLTV",
            "totalMaintenanceMargin",
        ],
    )
    return preprocess_dataframe(df)
