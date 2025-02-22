import pandas as pd

from crypto_pandas.order_schema import OrderSchema

df = pd.DataFrame(
    {
        "symbol": ["BTCUSDT", "BTCUSDT", "BTCUSDT"],
        "side": ["BUY", "BUY", "SELL"],
        "quantity": [1.3, 1.4, 2.9],
        "type": ["LIMIT", "MARKET", "LIMIT"],
        "price": [1.3, 1.4, 2.9],
    }
)
OrderSchema.validate(df)
df2 = pd.DataFrame(
    {
        "symbol": ["BTCUSDT", "BTCUSDT", "BTCUSDT"],
        "side": ["BUY", "BUY", "SELL"],
        "quantity": [1.3, 1.4, 2.9],
        "type": ["LIMIT", "MARKET", "LIMIT"],
        "price": [-1.3, 1.4, 2.9],
    }
)
OrderSchema.validate(df2)
