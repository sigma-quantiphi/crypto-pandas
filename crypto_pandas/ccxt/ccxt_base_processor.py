from dataclasses import dataclass, field
from typing import Dict, Any

import pandera as pa
from pandera.typing import Series

from crypto_pandas.base_processor import BaseProcessor
from crypto_pandas.order_schema import OrderSchema


class CCXTOrderSchema(pa.DataFrameModel):
    """Base schema for CCXT orders."""

    id: str = pa.Field(nullable=True, default=None)
    symbol: str = pa.Field()
    side: str = pa.Field(isin=["buy", "sell"])
    type: str = pa.Field(isin=["limit", "market", "stop_loss", "take_profit"])
    amount: float = pa.Field(gt=0)
    price: float = pa.Field(ge=0, nullable=True, default=None)
    params: Series[Dict[str, Any]]


@dataclass
class CCXTProcessor(BaseProcessor):
    order_schema: OrderSchema = field(default=CCXTOrderSchema)
