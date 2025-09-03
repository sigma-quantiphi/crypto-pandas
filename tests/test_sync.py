import os

import ccxt
import pytest
import pandas as pd
from dotenv import load_dotenv

from crypto_pandas.ccxt.ccxt_pandas_exchange import CCXTPandasExchange

load_dotenv()
symbol = "BNB/USDT:USDT"
sandbox_settings = {
    "apiKey": os.getenv("SANDBOX_API_KEY"),
    "secret": os.getenv("SANDBOX_API_SECRET"),
    "options": {
        "defaultType": "future",
        "loadAllOptions": True,
    },
}
settings = {
    "apiKey": os.getenv("API_KEY"),
    "secret": os.getenv("API_SECRET"),
    "options": {
        "defaultType": "future",
        "loadAllOptions": True,
    },
}
okx_settings = {
    "apiKey": os.getenv("OKX_API_KEY"),
    "secret": os.getenv("OKX_API_SECRET"),
    "password": os.getenv("OKX_API_PASSWORD"),
}
coinbase_settings = {
    "apiKey": os.getenv("COINBASE_API_KEY"),
    "secret": os.getenv("COINBASE_API_SECRET").replace("\\n", "\n"),
}


@pytest.fixture(scope="module")
def coinbase_exchange():
    exchange = ccxt.coinbase(coinbase_settings)
    return CCXTPandasExchange(exchange=exchange)


@pytest.fixture(scope="module")
def binance_exchange():
    exchange = ccxt.binance(settings)
    return CCXTPandasExchange(exchange=exchange)


@pytest.fixture(scope="module")
def sandbox_exchange():
    exchange = ccxt.binance(sandbox_settings)
    exchange.set_sandbox_mode(True)
    return CCXTPandasExchange(exchange=exchange)


@pytest.fixture(scope="module")
def okx_exchange():
    exchange = ccxt.okx(okx_settings)
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


def test_fetch_balance(binance_exchange):
    data = binance_exchange.fetch_balance()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_accounts(okx_exchange):
    data = okx_exchange.fetch_accounts()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_portfolios(coinbase_exchange):
    data = coinbase_exchange.fetch_portfolios()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)
    data = coinbase_exchange.fetch_portfolio_details(portfolioUuid=data["id"][0])
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_trading_fee(binance_exchange):
    data = binance_exchange.fetch_trading_fee(symbol=symbol)
    print(data)
    assert isinstance(data, dict)


def test_fetch_trading_fees(binance_exchange):
    data = binance_exchange.fetch_trading_fees()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_transfers(binance_exchange):
    data = binance_exchange.fetch_transfers()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_currencies(binance_exchange):
    data = binance_exchange.fetch_currencies()
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_deposit_withdraw_fees(binance_exchange):
    data = binance_exchange.fetch_deposit_withdraw_fees()
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


def test_fetch_status(binance_exchange):
    data = binance_exchange.fetch_status()
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


def test_fetch_greeks(binance_exchange):
    options_symbol = (
        binance_exchange.load_markets().query("type == 'option'")["symbol"].values[0]
    )
    data = binance_exchange.fetch_greeks(options_symbol)
    print(data)
    assert isinstance(data, dict)


def test_fetch_all_greeks(binance_exchange):
    data = binance_exchange.fetch_all_greeks()
    print(data.dropna(axis=1))
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


# def test_fetch_position(exchange):
#     data = exchange.fetch_position(symbol)
#     print(data)
#     assert isinstance(data, dict)


# def test_fetch_positions(exchange):
#     data = exchange.fetch_positions([symbol])
#     print(data)
#     print(data.dtypes)
#     assert isinstance(data, pd.DataFrame)


def test_fetch_ledger(binance_exchange):
    data = binance_exchange.fetch_ledger()
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


def test_fetch_last_prices(sandbox_exchange):
    data = sandbox_exchange.fetch_last_prices(symbols=[symbol])
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_open_interest(sandbox_exchange):
    data = sandbox_exchange.fetch_open_interest(symbol)
    print(data)
    assert isinstance(data, dict)


def test_fetch_open_interest_history(binance_exchange):
    data = binance_exchange.fetch_open_interest_history(symbol)
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


# def test_fetch_liquidations(bybit_exchange):
#     data = bybit_exchange.fetch_liquidations(symbol)
#     print(data)
#     print(data.dtypes)
#     assert isinstance(data, pd.DataFrame)


def test_fetch_leverages(sandbox_exchange):
    data = sandbox_exchange.fetch_leverages(symbols=[symbol])
    print(data)
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_long_short_ratio_history(binance_exchange):
    data = binance_exchange.fetch_long_short_ratio_history(symbol)
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


def test_fetch_convert_trade_history(binance_exchange):
    data = binance_exchange.fetch_convert_trade_history()
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


def test_fetch_convert_currencies(binance_exchange):
    data = binance_exchange.fetch_convert_currencies()
    print(data.dropna(axis=1))
    print(data.dtypes)
    assert isinstance(data, pd.DataFrame)


def test_fetch_cross_borrow_rate(binance_exchange):
    data = binance_exchange.fetch_cross_borrow_rate(code="BTC")
    print(data)
    assert isinstance(data, dict)


def test_create_order(sandbox_exchange):
    data = sandbox_exchange.create_order(
        symbol=symbol,
        type="limit",
        side="buy",
        amount=0.01,
        price=600.0,
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
            price=300.0,
        ),
        dict(
            side="sell",
            price=6000,
        ),
    ]
    orders = pd.DataFrame(orders)
    orders["cost"] = 7
    orders["type"] = "limit"
    orders["symbol"] = symbol
    data = sandbox_exchange.create_orders(orders=orders)
    print(data)
    assert isinstance(data, pd.DataFrame)
    data = sandbox_exchange.fetch_open_orders(symbol=symbol)
    print(data)
    assert isinstance(data, pd.DataFrame)
    if not data.empty:
        data["amount"] *= 2
        data = sandbox_exchange.edit_orders(orders=data)
        print(data)
        assert isinstance(data, pd.DataFrame)
        data = sandbox_exchange.cancel_all_orders(symbol=symbol)
        print(data)
        assert isinstance(data, pd.DataFrame)
