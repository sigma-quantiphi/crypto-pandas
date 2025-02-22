from dataclasses import dataclass

import pandera as pa
from crypto_pandas.binance.binance_base_processor import (
    BinanceBaseProcessor,
    BinanceBaseOrderSchema,
)


class BinanceUMFuturesOrderSchema(BinanceBaseOrderSchema):
    side: str = pa.Field(isin=["BUY", "SELL"], nullable=False)
    positionSide: str = pa.Field(
        isin=["BOTH", "LONG", "SHORT"], default="BOTH", nullable=True
    )
    type: str = pa.Field(
        isin=[
            "LIMIT",
            "MARKET",
            "STOP",
            "STOP_MARKET",
            "TAKE_PROFIT",
            "TAKE_PROFIT_MARKET",
            "TRAILING_STOP_MARKET",
        ],
        nullable=False,
    )
    timeInForce: str = pa.Field(isin=["GTC", "IOC", "FOK", "GTD"], nullable=True)
    quantity: float = pa.Field(ge=0, nullable=False)
    price: float = pa.Field(ge=0, nullable=True)
    reduceOnly: bool = pa.Field(default=False, nullable=True)
    newClientOrderId: str = pa.Field(
        str_matches=r"^[\.A-Z\:/a-z0-9_-]{1,36}$", nullable=True
    )
    stopPrice: float = pa.Field(ge=0, nullable=True)
    activationPrice: float = pa.Field(ge=0, nullable=True)
    callbackRate: float = pa.Field(ge=0.1, le=4, nullable=True)
    workingType: str = pa.Field(
        isin=["MARK_PRICE", "CONTRACT_PRICE"], default="CONTRACT_PRICE", nullable=True
    )
    priceProtect: bool = pa.Field(default=False, nullable=True)
    newOrderRespType: str = pa.Field(
        isin=["ACK", "RESULT"], default="ACK", nullable=True
    )
    priceMatch: str = pa.Field(
        isin=[
            "OPPONENT",
            "OPPONENT_5",
            "OPPONENT_10",
            "OPPONENT_20",
            "QUEUE",
            "QUEUE_5",
            "QUEUE_10",
            "QUEUE_20",
        ],
        nullable=True,
    )
    selfTradePreventionMode: str = pa.Field(
        isin=["NONE", "EXPIRE_TAKER", "EXPIRE_MAKER", "EXPIRE_BOTH"],
        default="NONE",
        nullable=True,
    )
    goodTillDate: pa.DateTime = pa.Field(ge=0, nullable=True)


@dataclass
class BinanceUMFuturesProcessor(BinanceBaseProcessor):
    order_schema = BinanceUMFuturesOrderSchema
