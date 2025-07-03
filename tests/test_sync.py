import os

import ccxt
import pytest
import pandas as pd
from dotenv import load_dotenv

from crypto_pandas.ccxt.ccxt_pandas_exchange import CCXTPandasExchange

load_dotenv()
symbol = "BNB/USDC:USDC"


@pytest.fixture(scope="module")
def binance_exchange():
    settings = {
        "apiKey": os.getenv("API_KEY"),
        "secret": os.getenv("API_SECRET"),
        "options": {
            "defaultType": "future",
        },
    }
    exchange = ccxt.binance(settings)
    return CCXTPandasExchange(exchange=exchange)


@pytest.fixture(scope="module")
def sandbox_exchange():
    settings = {
        "apiKey": os.getenv("SANDBOX_API_KEY"),
        "secret": os.getenv("SANDBOX_API_SECRET"),
        "options": {
            "defaultType": "future",
        },
    }
    exchange = ccxt.binance(settings)
    exchange.set_sandbox_mode(True)
    return CCXTPandasExchange(exchange=exchange)


@pytest.fixture(scope="module")
def bybit_exchange():
    return CCXTPandasExchange(exchange=ccxt.bybit())


def test_load_markets(sandbox_exchange):
    data = sandbox_exchange.load_markets()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_balance(sandbox_exchange):
    data = sandbox_exchange.fetch_balance()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_trading_fee(sandbox_exchange):
    data = sandbox_exchange.fetch_trading_fee(symbol=symbol)
    print(data)
    assert isinstance(data, dict)


def test_fetch_trading_fees(sandbox_exchange):
    data = sandbox_exchange.fetch_trading_fees()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_transfers(sandbox_exchange):
    data = sandbox_exchange.fetch_transfers()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_currencies(sandbox_exchange):
    data = sandbox_exchange.fetch_currencies()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_ticker(sandbox_exchange):
    data = sandbox_exchange.fetch_ticker(symbol)
    print(data)
    assert isinstance(data, dict)


def test_fetch_tickers(sandbox_exchange):
    data = sandbox_exchange.fetch_tickers([symbol, "ETH/USDT:USDT"])
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_order_book(sandbox_exchange):
    data = sandbox_exchange.fetch_order_book(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_ohlcv(sandbox_exchange):
    data = sandbox_exchange.fetch_ohlcv(symbol=symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_status(sandbox_exchange):
    data = sandbox_exchange.fetch_status()
    print(data)
    assert isinstance(data, dict)


def test_fetch_trades(sandbox_exchange):
    data = sandbox_exchange.fetch_trades(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_my_trades(sandbox_exchange):
    data = sandbox_exchange.fetch_my_trades(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_mark_price(sandbox_exchange):
    data = sandbox_exchange.fetch_mark_price(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, dict)


def test_mark_prices(sandbox_exchange):
    data = sandbox_exchange.fetch_mark_prices()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_markets(sandbox_exchange):
    data = sandbox_exchange.fetch_markets()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_isolated_borrow_rates(binance_exchange):
    data = binance_exchange.fetch_isolated_borrow_rates()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_orders(sandbox_exchange):
    data = sandbox_exchange.fetch_orders(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_open_orders(sandbox_exchange):
    data = sandbox_exchange.fetch_open_orders(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_closed_orders(sandbox_exchange):
    data = sandbox_exchange.fetch_closed_orders(symbol)
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


def test_fetch_ledger(sandbox_exchange):
    data = sandbox_exchange.fetch_ledger()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


# def test_fetch_withdrawals(exchange):
#     data = exchange.fetch_withdrawals(symbol=symbol)
#     print(data)
#     print(data.dtypes)
#     assert isinstance(data, pd.DataFrame)


def test_fetch_funding_rate_history(sandbox_exchange):
    data = sandbox_exchange.fetch_funding_rate_history(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_last_prices(binance_exchange):
    data = binance_exchange.fetch_last_prices(symbols=[symbol])
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_open_interest(sandbox_exchange):
    data = sandbox_exchange.fetch_open_interest(symbol)
    print(data)
    assert isinstance(data, dict)


def test_fetch_open_interest_history(sandbox_exchange):
    data = sandbox_exchange.fetch_open_interest_history(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


# def test_fetch_liquidations(bybit_exchange):
#     data = bybit_exchange.fetch_liquidations(symbol)
#     print(data)
#     print(data.dtypes)
#     assert isinstance(data, pd.DataFrame)


def test_fetch_leverages(sandbox_exchange):
    data = sandbox_exchange.fetch_leverages([symbol])
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_long_short_ratio_history(sandbox_exchange):
    data = sandbox_exchange.fetch_long_short_ratio_history(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_margin_adjustment_history(sandbox_exchange):
    data = sandbox_exchange.fetch_margin_adjustment_history(symbol=symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_my_liquidations(sandbox_exchange):
    data = sandbox_exchange.fetch_my_liquidations(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


# def test_fetch_option(exchange):
#     data = exchange.fetch_option(symbol)
#     print(data)
#     assert isinstance(data, dict)


def test_fetch_funding_rates(sandbox_exchange):
    data = sandbox_exchange.fetch_funding_rates([symbol])
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_convert_trade_history(sandbox_exchange):
    data = sandbox_exchange.fetch_convert_trade_history()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_bids_asks(sandbox_exchange):
    data = sandbox_exchange.fetch_bids_asks([symbol])
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_canceled_and_closed_orders(sandbox_exchange):
    data = sandbox_exchange.fetch_canceled_and_closed_orders(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_create_order(sandbox_exchange):
    data = sandbox_exchange.create_order(
        symbol=symbol,
        type="limit",
        side="buy",
        amount=0.01,
        price=600,
    )
    print(data)
    assert isinstance(data, dict)
    data = sandbox_exchange.fetch_order(id=data["id"], symbol=symbol)
    print(data)
    assert isinstance(data, dict)
    data = sandbox_exchange.cancel_order(id=data["id"], symbol=symbol)
    print(data)
    assert isinstance(data, dict)


def test_create_orders(sandbox_exchange):
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
    data = sandbox_exchange.create_orders(orders=orders)
    print(data)
    assert isinstance(data, pd.DataFrame)
    data = sandbox_exchange.fetch_open_orders(symbol=symbol)
    print(data)
    assert isinstance(data, pd.DataFrame)
    if not data.empty:
        data["amount"] = 0.02
        data = sandbox_exchange.edit_orders(orders=data)
        print(data)
        assert isinstance(data, pd.DataFrame)
        data = sandbox_exchange.cancel_all_orders(symbol=symbol)
        print(data)
        assert isinstance(data, pd.DataFrame)
