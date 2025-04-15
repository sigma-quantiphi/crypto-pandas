from typing import Optional

import pandera as pa


class OrderSchema(pa.DataFrameModel):
    """Base schema for orders (general for any exchange)."""

    id: Optional[str] = pa.Field(nullable=True, default=None)
    symbol: str = pa.Field()
    side: str = pa.Field(isin=["BUY", "SELL"])
    type: str = pa.Field(isin=["LIMIT", "MARKET"])
    price: Optional[float] = pa.Field(ge=0, nullable=True, default=None)
