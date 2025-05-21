from typing import Optional

import pandera as pa


class OrderSchema(pa.DataFrameModel):
    """Base schema for orders (general for any exchange)."""

    id: Optional[str] = pa.Field(nullable=True, default=None)
    symbol: str = pa.Field()
    side: str = pa.Field(isin=["buy", "sell"])
    type: str = pa.Field(isin=["limit", "market", "stop_loss", "take_profit"])
    amount: float = pa.Field(gt=0)
    price: Optional[float] = pa.Field(ge=0, nullable=True, default=None)
    params: Optional[dict] = pa.Field(nullable=True, default=None)
