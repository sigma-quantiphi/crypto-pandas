from dataclasses import dataclass, field
import pandera as pa
from crypto_pandas.binance.binance_base_processor import (
    BinanceBaseProcessor,
    BinanceBaseOrderSchema,
)


class BinanceOptionOrderSchema(BinanceBaseOrderSchema):
    price: float = pa.Field(gt=0)
    timeInForce: str = pa.Field(
        isin=["GTC", "IOC", "FOK"], default="GTC", nullable=True
    )
    reduceOnly: bool = pa.Field(nullable=True, default=False)
    postOnly: bool = pa.Field(nullable=True, default=False)
    newOrderRespType: str = pa.Field(
        isin=["ACK", "RESULT"], default="ACK", nullable=True
    )
    clientOrderId: str = pa.Field(nullable=True, default=None)
    isMmp: bool = pa.Field(nullable=True, default=None)


@dataclass
class BinanceOptionsProcessor(BinanceBaseProcessor):
    order_schema: BinanceBaseOrderSchema = field(default=BinanceOptionOrderSchema)
