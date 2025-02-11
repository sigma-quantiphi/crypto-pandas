import pandas as pd

from crypto_pandas.utils.pandas_utils import preprocess_dataframe
from crypto_pandas.utils.utils import prepare_requests_parameters

int_datetime_columns = {"timestamp", "creationTimestamp", "fundingRateTimestamp"}
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


def prepare_requests_parameters_bybit(params: dict) -> dict:
    return prepare_requests_parameters(
        params, date_time_to_int_keys=int_datetime_columns
    )


def preprocess_dataframe_bybit(data: pd.DataFrame) -> pd.DataFrame:
    return preprocess_dataframe(
        data, int_datetime_columns=int_datetime_columns, numeric_columns=numeric_columns
    )


def market_tickers_response_to_dataframe(data: dict) -> pd.DataFrame:
    data = pd.json_normalize(data=data["result"], record_path="list", meta=["category"])
    return preprocess_dataframe(
        data, int_datetime_columns=int_datetime_columns, numeric_columns=numeric_columns
    )


def account_wallet_balance_response_to_dataframe(data: dict) -> pd.DataFrame:
    data = pd.json_normalize(
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
    return preprocess_dataframe(
        data, int_datetime_columns=int_datetime_columns, numeric_columns=numeric_columns
    )
