import grequests
import pandas as pd
from crypto_pandas.binance.markets import depth_to_dataframe


def get_options_orderbooks(symbols: list[str]) -> pd.DataFrame:
    rs = (
        grequests.get(
            "https://eapi.binance.com/eapi/v1/depth", params={"symbol": symbol}
        )
        for symbol in symbols
    )
    data = grequests.map(rs)
    data = [{**x.json(), "symbol": symbol} for x, symbol in zip(data, symbols)]
    return depth_to_dataframe(data)


possible_options_columns = [
    "symbol",
    "side",
    "quantity",
    "price",
    "timeInForce",
    "reduceOnly",
    "postOnly",
    "newOrderRespType",
    "clientOrderId",
    "isMmp",
]


def options_orders_to_dict(orders: pd.DataFrame) -> list:
    columns = [x for x in possible_options_columns if x in orders.columns]
    data = orders[columns].copy()
    data["type"] = "LIMIT"
    data[["quantity", "price"]] = data[["quantity", "price"]].astype(str)
    return data.to_dict("records")
