import pandas as pd
from crypto_pandas.utils.utils import timestamp_to_int
from crypto_pandas.utils.errors import check_missing_element

mandatory_order_columns = [
    "symbol",
    "side",
    "type",
    "quantity",
]
possible_order_columns = mandatory_order_columns + [
    "price",
    "timeInForce",
    "reduceOnly",
    "postOnly",
    "newOrderRespType",
    "clientOrderId",
    "isMmp",
]


def orders_to_dict(
    orders: pd.DataFrame, quantity_tick_size: int = 2, price_tick_size: int = 2
) -> list:
    columns = orders.columns
    check_missing_element(mandatory_order_columns, columns)
    columns = [x for x in possible_order_columns if x in columns]
    data = orders[columns].copy()
    data["quantity"] = data["quantity"].apply(lambda x: f"{x:.{quantity_tick_size}f}")
    if "price" in columns:
        data["price"] = data["price"].apply(lambda x: f"{x:.{price_tick_size}f}")
    if "goodTillDate" in columns:
        data["goodTillDate"] = timestamp_to_int(data["goodTillDate"])
    return data.to_dict("records")
