mandatory_order_columns = [
    "symbol",
    "side",
    "type",
    "quantity",
    "timeInForce",
]
possible_order_columns = mandatory_order_columns + [
    "price",
    "reduceOnly",
    "postOnly",
    "newOrderRespType",
    "clientOrderId",
    "isMmp",
]


def orders_to_dict(orders: pd.DataFrame) -> list:
    check_missing_element(orders.columns, mandatory_order_columns)
    columns = [x for x in possible_order_columns if x in orders.columns]
    data = orders[columns].copy()
    data[["quantity", "price"]] = data[["quantity", "price"]].astype(str)
    return data.to_dict("records")
