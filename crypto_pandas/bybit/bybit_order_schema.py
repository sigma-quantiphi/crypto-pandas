import pandera as pa

from crypto_pandas.order_schema import OrderSchema


class BybitBatchOrderSchema(OrderSchema):
    """Schema for Bybit Batch Place Order."""

    category: str = pa.Field(isin=["linear", "option", "spot", "inverse"])
    symbol: str = pa.Field()
    side: str = pa.Field(isin=["Buy", "Sell"])
    orderType: str = pa.Field(isin=["Market", "Limit"])
    qty: str = pa.Field()  # Quantity as a string to match API spec

    # Optional fields
    isLeverage: int = pa.Field(nullable=True, isin=[0, 1], default=0)  # Spot only
    marketUnit: str = pa.Field(nullable=True, isin=["baseCoin", "quoteCoin"])
    price: str = pa.Field(nullable=True)
    triggerDirection: int = pa.Field(nullable=True, isin=[1, 2])
    orderFilter: str = pa.Field(nullable=True, isin=["Order", "tpslOrder", "StopOrder"])
    triggerPrice: str = pa.Field(nullable=True)
    triggerBy: str = pa.Field(
        nullable=True, isin=["LastPrice", "IndexPrice", "MarkPrice"]
    )
    orderIv: str = pa.Field(nullable=True)
    timeInForce: str = pa.Field(
        nullable=True, isin=["GTC", "IOC", "FOK", "PostOnly"], default="GTC"
    )
    positionIdx: int = pa.Field(nullable=True, isin=[0, 1, 2])
    orderLinkId: str = pa.Field(nullable=True)
    reduceOnly: bool = pa.Field(nullable=True)
    closeOnTrigger: bool = pa.Field(nullable=True)
    takeProfit: str = pa.Field(nullable=True)
    stopLoss: str = pa.Field(nullable=True)
    tpTriggerBy: str = pa.Field(
        nullable=True, isin=["LastPrice", "IndexPrice", "MarkPrice"]
    )
    slTriggerBy: str = pa.Field(
        nullable=True, isin=["LastPrice", "IndexPrice", "MarkPrice"]
    )
    tpLimitPrice: str = pa.Field(nullable=True)
    slLimitPrice: str = pa.Field(nullable=True)
    tpOrderType: str = pa.Field(nullable=True, isin=["Market", "Limit"])
    slOrderType: str = pa.Field(nullable=True, isin=["Market", "Limit"])
    tpslMode: str = pa.Field(nullable=True, isin=["Full", "Partial"])
    mmp: bool = pa.Field(nullable=True)
    smpType: str = pa.Field(
        nullable=True, isin=["None", "CancelMaker", "CancelTaker", "CancelBoth"]
    )
