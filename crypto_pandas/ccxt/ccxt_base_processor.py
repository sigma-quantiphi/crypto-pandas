from dataclasses import dataclass, field
from typing import Optional

import pandera as pa

from crypto_pandas.base_processor import BaseProcessor
from crypto_pandas.order_schema import OrderSchema


class CCXTOrderSchema(pa.DataFrameModel):
    """Base schema for CCXT orders."""

    id: Optional[str] = pa.Field(nullable=True, default=None)
    symbol: str = pa.Field()
    side: str = pa.Field(isin=["buy", "sell"])
    type: str = pa.Field(isin=["limit", "market", "stop_loss", "take_profit"])
    amount: float = pa.Field(gt=0)
    price: Optional[float] = pa.Field(ge=0, nullable=True, default=None)
    params: Optional[dict] = pa.Field(nullable=True, default=None)


@dataclass
class CCXTProcessor(BaseProcessor):
    order_schema: OrderSchema = field(default=CCXTOrderSchema)
