import pandas as pd
from crypto_pandas.utils.pandas_utils import date_time_column_to_int
from crypto_pandas.utils.checks import (
    check_missing_column,
    check_order_types,
    check_sides,
)

# Mandatory and possible columns for options and futures
mandatory_options_columns = {
    "symbol",
    "side",
    "type",
    "quantity",
    "price",
}
possible_options_columns = mandatory_options_columns | {
    "timeInForce",
    "reduceOnly",
    "postOnly",
    "newOrderRespType",
    "clientOrderId",
    "isMmp",
}
mandatory_futures_columns = {
    "symbol",
    "side",
    "type",
    "quantity",
}
possible_futures_columns = mandatory_futures_columns | {
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
}

# Allowed values for order parameters
allowed_sides = {"BUY", "SELL"}
allowed_options_types = {"LIMIT"}
allowed_futures_types = {
    "LIMIT",
    "MARKET",
    "STOP_LOSS",
    "STOP_LOSS_LIMIT",
    "TAKE_PROFIT",
    "TAKE_PROFIT_LIMIT",
    "LIMIT_MAKER",
}
allowed_options_time_in_force = {"GTC", "IOC", "FOK"}
allowed_futures_time_in_force = allowed_options_time_in_force | {"GTD"}
allowed_options_new_order_resp_type = {"ACK", "RESULT"}


def orders_to_dict(
    orders: pd.DataFrame,
) -> list:
    check_sides(orders["side"])
    data["quantity"] = data.apply(
        lambda x: format_value(x["quantity"], x["stepSize"]), axis=1
    )
    if "price" in columns:
        data["price"] = data.apply(
            lambda x: format_value(x["price"], x["tickSize"]), axis=1
        )
    if "goodTillDate" in columns:
        data["goodTillDate"] = date_time_column_to_int(data["goodTillDate"])
    if "reduceOnly" in columns:
        data["reduceOnly"] = data["reduceOnly"].replace({True: "true", False: "false"})
    if "postOnly" in columns:
        data["postOnly"] = data["postOnly"].replace({True: "true", False: "false"})
    return orders.to_dict("records")


def options_orders_to_dict(orders: pd.DataFrame) -> list:
    check_missing_column(mandatory_options_columns, orders.columns)
    check_order_types(orders["type"], allowed_options_types)
    check_order_types(orders["timeInForce"], allowed_options_time_in_force)
    columns = [x for x in possible_options_columns if x in orders.columns]
    return orders_to_dict(
        orders=orders[columns].copy(),
    )


def futures_orders_to_dict(orders: pd.DataFrame) -> list:
    check_missing_column(mandatory_futures_columns, orders.columns)
    check_order_types(orders["type"], allowed_futures_types)
    check_order_types(orders["timeInForce"], allowed_futures_time_in_force)
    columns = [x for x in possible_futures_columns if x in orders.columns]
    return orders_to_dict(
        orders=orders[columns].copy(),
    )
