import os

import ccxt
import pytest
import pandas as pd
from dotenv import load_dotenv

from crypto_pandas.ccxt.ccxt_pandas_exchange import CCXTPandasExchange

load_dotenv()
settings = {
    "apiKey": os.getenv("API_KEY_READ"),
    "secret": os.getenv("API_SECRET_READ"),
    "options": {
        "defaultType": "future",
    },
}


@pytest.fixture(scope="module")
def exchange():
    return CCXTPandasExchange(exchange=ccxt.binance(settings))


def test_load_markets(exchange):
    data = exchange.load_markets()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_balance(exchange):
    data = exchange.fetch_balance()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_currencies(exchange):
    data = exchange.fetch_currencies()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_ticker(exchange):
    data = exchange.fetch_ticker("BTC/USDT:USDT")
    print(data)
    print(data.dtypes)
    assert isinstance(data, dict)


def test_fetch_tickers(exchange):
    data = exchange.fetch_tickers(["BTC/USDT:USDT", "ETH/USDT:USDT"])
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_order_book(exchange):
    data = exchange.fetch_order_book("BTC/USDT:USDT")
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_ohlcv(exchange):
    data = exchange.fetch_ohlcv("BTC/USDT:USDT")
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_status(exchange):
    data = exchange.fetch_status()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_trades(exchange):
    data = exchange.fetch_trades("BTC/USDT:USDT")
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_my_trades(exchange):
    data = exchange.fetch_my_trades("BNB/USDC:USDC")
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_orders(exchange):
    data = exchange.fetch_orders("BNB/USDC:USDC")
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_open_orders(exchange):
    data = exchange.fetch_open_orders("BNB/USDC:USDC")
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_closed_orders(exchange):
    data = exchange.fetch_closed_orders("BNB/USDC:USDC")
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_order(exchange):
    try:
        data = exchange.fetch_order("1912589824", symbol="BNB/USDC:USDC")
    except Exception:
        data = pd.DataFrame()
    print(data)
    print(data.dtypes)
    assert isinstance(data, dict)


def test_create_order(exchange):
    # Skip this live test unless using sandbox or mocked exchange
    pass


def test_cancel_order(exchange):
    # Skip this live test unless using sandbox or mocked exchange
    pass
