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
