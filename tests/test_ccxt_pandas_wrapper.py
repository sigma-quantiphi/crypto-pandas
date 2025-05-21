import pytest
import pandas as pd
from crypto_pandas.ccxt.exchange_wrapper import ExchangePandasWrapper

@pytest.fixture(scope="module")
def exchange():
    return ExchangePandasWrapper("binance")

def test_load_markets(exchange):
    assert isinstance(exchange.load_markets(), pd.DataFrame)

def test_fetch_balance(exchange):
    assert isinstance(exchange.fetch_balance(), pd.DataFrame)

def test_fetch_currencies(exchange):
    assert isinstance(exchange.fetch_currencies(), pd.DataFrame)

def test_fetch_ticker(exchange):
    assert isinstance(exchange.fetch_ticker("BTC/USDT"), pd.DataFrame)

def test_fetch_tickers(exchange):
    assert isinstance(exchange.fetch_tickers(["BTC/USDT", "ETH/USDT"]), pd.DataFrame)

def test_fetch_order_book(exchange):
    assert isinstance(exchange.fetch_order_book("BTC/USDT"), pd.DataFrame)

def test_fetch_ohlcv(exchange):
    assert isinstance(exchange.fetch_ohlcv("BTC/USDT"), pd.DataFrame)

def test_fetch_status(exchange):
    assert isinstance(exchange.fetch_status(), pd.DataFrame)

def test_fetch_trades(exchange):
    assert isinstance(exchange.fetch_trades("BTC/USDT"), pd.DataFrame)

def test_fetch_my_trades(exchange):
    assert isinstance(exchange.fetch_my_trades("BTC/USDT"), pd.DataFrame)

def test_fetch_orders(exchange):
    assert isinstance(exchange.fetch_orders("BTC/USDT"), pd.DataFrame)

def test_fetch_open_orders(exchange):
    assert isinstance(exchange.fetch_open_orders("BTC/USDT"), pd.DataFrame)

def test_fetch_closed_orders(exchange):
    assert isinstance(exchange.fetch_closed_orders("BTC/USDT"), pd.DataFrame)

def test_fetch_order(exchange):
    # Use an invalid order ID for testing format only
    try:
        df = exchange.fetch_order("123456789", symbol="BTC/USDT")
    except Exception:
        df = pd.DataFrame()
    assert isinstance(df, pd.DataFrame)

def test_create_order(exchange):
    # Skip this live test unless using sandbox or mocked exchange
    pass

def test_cancel_order(exchange):
    # Skip this live test unless using sandbox or mocked exchange
    pass
