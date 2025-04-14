from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import pandera as pa
from crypto_pandas.base_processor import BaseProcessor
from crypto_pandas.order_schema import OrderSchema
from crypto_pandas.utils.pandas_utils import date_time_columns_to_int


class BinanceBaseOrderSchema(OrderSchema):
    quantity: float = pa.Field(gt=0)
    price: float = pa.Field(gt=0)
    stepSize: float = pa.Field(ge=0)


@dataclass
class BinanceBaseProcessor(BaseProcessor):
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
        ),
        init=False,
    )
    str_to_datetime_fields: tuple = field(default=None, init=False)
    numeric_fields: tuple = field(
        default=(
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
        ),
        init=False,
    )
    bool_fields: tuple = field(
        default=("isAutoAddMargin",),
        init=False,
    )
    recv_window_field_name: str = field(
        default="recvWindow",
        init=False,
    )
    ohlcv_fields: tuple = field(
        default=(
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
        ),
        init=False,
    )

    def exchange_info_to_dataframe_binance(
        self, data: list, record_path: str = "symbols"
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
        return self.preprocess_dataframe(data=data)

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

    def format_value(self, value: float, step_size: float = 0.001) -> str:
        """Rounds the data according to the provided step size"""
        if step_size >= 1:
            formatted_value = str(int(round(value / step_size) * step_size))
        else:
            decimals = abs(int(np.log10(step_size)))
            formatted_value = f"{value:.{decimals}f}"
        return formatted_value

    def format_orders(
        self, orders: pd.DataFrame, quantity_field_name: str = "quantity"
    ) -> list:
        data = orders.copy()
        data = date_time_columns_to_int(data)
        data[quantity_field_name] = data.apply(
            lambda x: self.format_value(x[quantity_field_name], x["stepSize"]), axis=1
        )
        if "price" in data.columns:
            data["price"] = data.apply(
                lambda x: self.format_value(x["price"], x["tickSize"]), axis=1
            )
        return data.drop(columns=["stepSize", "tickSize"]).to_dict("records")

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
