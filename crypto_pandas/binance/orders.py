import pandas as pd
from crypto_pandas.utils.pandas_utils import date_time_column_to_int
from crypto_pandas.utils.checks import check_missing_element

mandatory_options_columns = [
    "symbol",
    "side",
    "type",
    "quantity",
    "price",
]
possible_options_columns = mandatory_options_columns + [
    "timeInForce",
    "reduceOnly",
    "postOnly",
    "newOrderRespType",
    "clientOrderId",
    "isMmp",
]
mandatory_futures_columns = ["symbol", "side", "type", "quantity"]
possible_futures_columns = [
    "positionSide",
    "timeInForce",
    "reduceOnly",
    "price",
    "newClientOrderId",
    "stopPrice",
    "activationPrice",
    "callbackRate",
    "workingType",
    "priceProtect",
    "newOrderRespType",
    "priceMatch",
    "selfTradePreventionMode",
    "goodTillDate",
]


def orders_to_dict(
    orders: pd.DataFrame,
    mandatory_columns: list,
    possible_columns: list,
    quantity_tick_size: int = 2,
    price_tick_size: int = 3,
) -> list:
    columns = orders.columns
    check_missing_element(mandatory_columns, columns)
    columns = [x for x in possible_columns if x in columns]
    data = orders[columns].copy()
    data["quantity"] = data["quantity"].apply(lambda x: f"{x:.{quantity_tick_size}f}")
    if "price" in columns:
        data["price"] = data["price"].apply(lambda x: f"{x:.{price_tick_size}f}")
    if "goodTillDate" in columns:
        data["goodTillDate"] = date_time_column_to_int(data["goodTillDate"])
    if "reduceOnly" in columns:
        data["reduceOnly"] = data["reduceOnly"].replace({True: "true", False: "false"})
    if "postOnly" in columns:
        data["postOnly"] = data["postOnly"].replace({True: "true", False: "false"})
    return data.to_dict("records")


def options_orders_to_dict(orders: pd.DataFrame) -> list:
    return orders_to_dict(
        orders=orders,
        mandatory_columns=mandatory_options_columns,
        possible_columns=possible_options_columns,
        quantity_tick_size=2,
        price_tick_size=3,
    )


def futures_orders_to_dict(orders: pd.DataFrame) -> list:
    return orders_to_dict(
        orders=orders,
        mandatory_columns=mandatory_futures_columns,
        possible_columns=possible_futures_columns,
        quantity_tick_size=2,
        price_tick_size=3,
    )
