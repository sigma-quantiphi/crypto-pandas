import ccxt
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Any, Dict, Union
from ccxt.base.exchange import Exchange
from crypto_pandas.ccxt.procesor import CCXTProcessor

ccxt_processor = CCXTProcessor()


@dataclass
class ExchangePandasWrapper:
    _exchange: Exchange

    def __init__(self, exchange_name: str = "binance", **kwargs: Any) -> None:
        self._exchange = getattr(ccxt, exchange_name)(**kwargs)

    def load_markets(self, params: dict | None = None) -> pd.DataFrame:
        data = self._exchange.load_markets(params=params or {})
        return ccxt_processor.markets_to_dataframe(data)

    def fetch_balance(self, params: dict | None = None) -> pd.DataFrame:
        data = self._exchange.fetch_balance(params=params or {})
        return ccxt_processor.balances_to_dataframe(data)

    def fetch_currencies(self, params: dict | None = None) -> pd.DataFrame:
        data = self._exchange.fetch_currencies(params=params or {})
        return ccxt_processor.response_(data)

    def fetch_ticker(self, symbol: str, params: dict | None = None) -> pd.DataFrame:
        data = self._exchange.fetch_ticker(symbol, params=params or {})
        return ccxt_processor.ticker_to_dataframe(data)

    def fetch_tickers(
        self, symbols: list[str] | None = None, params: dict | None = None
    ) -> pd.DataFrame:
        data = self._exchange.fetch_tickers(symbols=symbols, params=params or {})
        return ccxt_processor.tickers_to_dataframe(data)

    def fetch_order_book(
        self, symbol: str, limit: int | None = None, params: dict | None = None
    ) -> pd.DataFrame:
        data = self._exchange.fetch_order_book(symbol, limit=limit, params=params or {})
        return ccxt_processor.order_book_to_dataframe(data)

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        since: int | None = None,
        limit: int | None = None,
        params: dict | None = None,
    ) -> pd.DataFrame:
        data = self._exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since=since,
            limit=limit,
            params=params or {},
        )
        return ccxt_processor.ohlcv_to_dataframe(data)

    def fetch_status(self, params: dict | None = None) -> pd.DataFrame:
        data = self._exchange.fetch_status(params=params or {})
        return ccxt_processor.status_to_dataframe(data)

    def fetch_trades(
        self,
        symbol: str,
        since: int | None = None,
        limit: int | None = None,
        params: dict | None = None,
    ) -> pd.DataFrame:
        data = self._exchange.fetch_trades(
            symbol, since=since, limit=limit, params=params or {}
        )
        return ccxt_processor.trades_to_dataframe(data)

    def fetch_my_trades(
        self,
        symbol: str,
        since: int | None = None,
        limit: int | None = None,
        params: dict | None = None,
    ) -> pd.DataFrame:
        data = self._exchange.fetch_my_trades(
            symbol, since=since, limit=limit, params=params or {}
        )
        return ccxt_processor.trades_to_dataframe(data)

    def fetch_orders(
        self,
        symbol: str | None = None,
        since: int | None = None,
        limit: int | None = None,
        params: dict | None = None,
    ) -> pd.DataFrame:
        data = self._exchange.fetch_orders(
            symbol=symbol, since=since, limit=limit, params=params or {}
        )
        return ccxt_processor.orders_to_dataframe(data)

    def fetch_open_orders(
        self,
        symbol: str | None = None,
        since: int | None = None,
        limit: int | None = None,
        params: dict | None = None,
    ) -> pd.DataFrame:
        data = self._exchange.fetch_open_orders(
            symbol=symbol, since=since, limit=limit, params=params or {}
        )
        return ccxt_processor.orders_to_dataframe(data)

    def fetch_closed_orders(
        self,
        symbol: str | None = None,
        since: int | None = None,
        limit: int | None = None,
        params: dict | None = None,
    ) -> pd.DataFrame:
        data = self._exchange.fetch_closed_orders(
            symbol=symbol, since=since, limit=limit, params=params or {}
        )
        return ccxt_processor.orders_to_dataframe(data)

    def fetch_order(
        self, id: str, symbol: str | None = None, params: dict | None = None
    ) -> pd.DataFrame:
        data = self._exchange.fetch_order(id, symbol=symbol, params=params or {})
        return ccxt_processor.order_to_dataframe(data)

    def create_order(
        self,
        symbol: str,
        type: str,
        side: str,
        amount: float,
        price: float | None = None,
        params: dict | None = None,
    ) -> pd.DataFrame:
        data = self._exchange.create_order(
            symbol, type, side, amount, price=price, params=params or {}
        )
        return ccxt_processor.order_to_dataframe(data)

    def cancel_order(
        self, id: str, symbol: str | None = None, params: dict | None = None
    ) -> pd.DataFrame:
        data = self._exchange.cancel_order(id, symbol=symbol, params=params or {})
        return ccxt_processor.order_to_dataframe(data)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._exchange, name)
