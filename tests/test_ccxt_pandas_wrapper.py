import os

import ccxt
import pytest
import pandas as pd
from dotenv import load_dotenv

from crypto_pandas.ccxt.ccxt_pandas_exchange import CCXTPandasExchange

load_dotenv()
settings = {
    "apiKey": os.getenv("API_KEY"),
    "secret": os.getenv("API_SECRET"),
    "options": {
        "defaultType": "future",
    },
}
symbol = "BNB/USDC:USDC"


@pytest.fixture(scope="module")
def exchange():
    return CCXTPandasExchange(exchange=ccxt.binance(settings))


@pytest.fixture(scope="module")
def bybit_exchange():
    return CCXTPandasExchange(exchange=ccxt.bybit())


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


def test_fetch_transfers(exchange):
    data = exchange.fetch_transfers()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_currencies(exchange):
    data = exchange.fetch_currencies()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_ticker(exchange):
    data = exchange.fetch_ticker(symbol)
    print(data)
    assert isinstance(data, dict)


def test_fetch_tickers(exchange):
    data = exchange.fetch_tickers([symbol, "ETH/USDT:USDT"])
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_order_book(exchange):
    data = exchange.fetch_order_book(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_ohlcv(exchange):
    data = exchange.fetch_ohlcv(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_status(exchange):
    data = exchange.fetch_status()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_trades(exchange):
    data = exchange.fetch_trades(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_my_trades(exchange):
    data = exchange.fetch_my_trades(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_orders(exchange):
    data = exchange.fetch_orders(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_open_orders(exchange):
    data = exchange.fetch_open_orders(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_closed_orders(exchange):
    data = exchange.fetch_closed_orders(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_greeks(bybit_exchange):
    options_symbol = (
        bybit_exchange.load_markets().query("type == 'option'")["symbol"].values[0]
    )
    data = bybit_exchange.fetch_greeks(options_symbol)
    print(data)
    assert isinstance(data, dict)


# def test_fetch_position(exchange):
#     data = exchange.fetch_position(symbol)
#     print(data)
#     assert isinstance(data, dict)


# def test_fetch_positions(exchange):
#     data = exchange.fetch_positions([symbol])
#     print(data)
#     print(data.dtypes)
#     assert isinstance(data, pd.DataFrame)


def test_fetch_ledger(exchange):
    data = exchange.fetch_ledger()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


# def test_fetch_withdrawals(exchange):
#     data = exchange.fetch_withdrawals(symbol=symbol)
#     print(data)
#     print(data.dtypes)
#     assert isinstance(data, pd.DataFrame)


def test_fetch_funding_rate_history(exchange):
    data = exchange.fetch_funding_rate_history(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_open_interest(exchange):
    data = exchange.fetch_open_interest(symbol)
    print(data)
    assert isinstance(data, dict)


def test_fetch_open_interest_history(exchange):
    data = exchange.fetch_open_interest_history(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


# def test_fetch_liquidations(bybit_exchange):
#     data = bybit_exchange.fetch_liquidations(symbol)
#     print(data)
#     print(data.dtypes)
#     assert isinstance(data, pd.DataFrame)


def test_fetch_leverages(exchange):
    data = exchange.fetch_leverages([symbol])
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_long_short_ratio_history(exchange):
    data = exchange.fetch_long_short_ratio_history(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_margin_adjustment_history(exchange):
    data = exchange.fetch_margin_adjustment_history(symbol=symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_my_liquidations(exchange):
    data = exchange.fetch_my_liquidations(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


# def test_fetch_option(exchange):
#     data = exchange.fetch_option(symbol)
#     print(data)
#     assert isinstance(data, dict)


def test_fetch_funding_rates(exchange):
    data = exchange.fetch_funding_rates([symbol])
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_convert_trade_history(exchange):
    data = exchange.fetch_convert_trade_history()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_bids_asks(exchange):
    data = exchange.fetch_bids_asks([symbol])
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_canceled_and_closed_orders(exchange):
    data = exchange.fetch_canceled_and_closed_orders(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_create_order(exchange):
    data = exchange.create_order(
        symbol=symbol,
        type="limit",
        side="buy",
        amount=0.01,
        price=600,
    )
    print(data)
    data = exchange.fetch_order(id=data["id"], symbol=symbol)
    print(data)
    data = exchange.cancel_order(id=data["id"], symbol=symbol)
    print(data)
    assert isinstance(data, dict)


def test_create_orders(exchange):
    orders = [
        dict(
            side="buy",
            price=600,
        ),
        dict(
            side="sell",
            price=6000,
        ),
    ]
    orders = pd.DataFrame(orders)
    orders["notional"] = 7
    orders["type"] = "limit"
    orders["symbol"] = symbol
    data = exchange.create_orders(orders=orders)
    print(data)
    data = exchange.fetch_open_orders(symbol=symbol)
    print(data)
    data["amount"] = 0.02
    data = exchange.edit_orders(orders=data)
    print(data)
    data = exchange.cancel_all_orders(symbol=symbol)
    print(data)
    assert isinstance(data, pd.DataFrame)
