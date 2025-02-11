import pandas as pd

from crypto_pandas.ccxt.preprocessing import preprocess_dataframe_ccxt


def orders_to_dataframe(data: list) -> pd.DataFrame:
    trades = pd.json_normalize(
        data=data,
        record_path="trades",
        meta=[
            "id",
            "clientOrderId",
            "timestamp",
            "datetime",
            "lastTradeTimestamp",
            "lastUpdateTimestamp",
            "symbol",
            "type",
            "timeInForce",
            "postOnly",
            "reduceOnly",
            "side",
            "price",
            "triggerPrice",
            "amount",
            "cost",
            "average",
            "filled",
            "remaining",
            "status",
            "fee",
            "fees",
            "stopPrice",
            "takeProfitPrice",
            "stopLossPrice",
        ],
    )
    orders = pd.DataFrame(data=data)
    if not trades.empty:
        orders = orders.merge(trades, how="outer")
    return preprocess_dataframe_ccxt(orders)
