from dataclasses import dataclass, field
from typing import Union

import pandas as pd

from crypto_pandas.base_processor import BaseProcessor


@dataclass
class BybitProcessor(BaseProcessor):
    datetime_to_int_fields: tuple = field(
        default=(
            "startTime",
            "endTime",
            "beginTime",
            "subscriptionStartTime",
        ),
        init=False,
    )
    int_to_datetime_fields: tuple = field(
        default=(
            "timestamp",
            "creationTimestamp",
            "fundingRateTimestamp",
        ),
        init=False,
    )
    str_to_datetime_fields: tuple = field(default=None, init=False)
    numeric_fields: tuple = field(
        default=(
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
        ),
        init=False,
    )
    ohlcv_fields: tuple = field(
        default=(
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover",
            "category",
            "symbol",
        ),
        init=False,
    )

    def orderbook_to_dataframe(self, data: Union[dict, list]) -> pd.DataFrame:
        df = []
        for side, side_name in zip(["a", "b"], ["asks", "bids"]):
            df_temp = pd.json_normalize(
                data=data["result"],
                record_path=side,
                meta=["s", "ts", "u", "seq", "cts"],
            )
            df_temp["side"] = side_name
            df.append(df_temp)
        if df:
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
            return self.preprocess_dataframe(df)

    def ohlcv_to_dataframe(self, data: dict) -> pd.DataFrame:
        df = pd.json_normalize(
            data=data["result"], record_path="list", meta=["category", "symbol"]
        )
        df.columns = self.ohlcv_fields
        return self.preprocess_dataframe(df)

    def market_tickers_to_dataframe(self, data: dict) -> pd.DataFrame:
        data = pd.json_normalize(
            data=data["result"], record_path="list", meta=["category"]
        )
        return self.preprocess_dataframe(data)

    def order_to_dataframe(self, data: dict) -> pd.DataFrame:
        data = pd.json_normalize(
            data=data,
            meta=[
                "symbol",
                "orderId",
                "orderListId",
                "clientOrderId",
                "transactTime",
                "price",
                "origQty",
                "executedQty",
                "origQuoteOrderQty",
                "cummulativeQuoteQty",
                "status",
                "timeInForce",
                "type",
                "side",
                "workingTime",
                "selfTradePreventionMode",
            ],
            record_path="fills",
            record_prefix="fills.",
        )
        return self.preprocess_dataframe(data)

    def account_to_dataframe(self, data: dict) -> pd.DataFrame:
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
        return self.preprocess_dataframe(data)

    def account_wallet_balance_to_dataframe(self, data: dict) -> pd.DataFrame:
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
        return self.preprocess_dataframe(data)
