from typing import Optional

import pandera.pandas as pa


class OrderSchema(pa.DataFrameModel):
    """Base schema for orders (general for any exchange)."""

    id: Optional[str] = pa.Field(
        nullable=True, default=None, description="Exchange-assigned order ID"
    )
    symbol: str = pa.Field(description="Unified CCXT market symbol")
    side: str = pa.Field(isin=["buy", "sell"])
    type: str = pa.Field(isin=["limit", "market", "stop_loss", "take_profit"])
    amount: Optional[float] = pa.Field(gt=0)
    price: Optional[float] = pa.Field(ge=0, nullable=True, default=None)
    params: Optional[dict] = pa.Field(nullable=True, default=None)

    @classmethod
    def validate_price_for_limit_orders(cls, df):
        limit_orders = df.query("type != 'market'")
        if limit_orders["price"].isnull().any():
            raise ValueError("Non market orders must include a price.")
