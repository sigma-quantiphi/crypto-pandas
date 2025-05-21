from typing import Literal

import ccxt
import pandas as pd
from dataclasses import dataclass, field

from ccxt import Exchange

from crypto_pandas.ccxt.base_processor import BaseProcessor

ccxt_processor = BaseProcessor()


@dataclass
class CCXTPandasExchange(Exchange):
    exchange: Exchange = field(default_factory=ccxt.binance)

    def load_markets(self, reload: bool = False, params: dict = {}) -> pd.DataFrame:
        data = self.exchange.load_markets(reload=reload, params=params)
        return ccxt_processor.markets_to_dataframe(data)

    def fetch_balance(self, params: dict = {}) -> pd.DataFrame:
        data = self.exchange.fetch_balance(params=params)
        return ccxt_processor.balance_to_dataframe(data)

    def fetch_currencies(self, params: dict = {}) -> pd.DataFrame:
        data = self.exchange.fetch_currencies(params=params)
        return ccxt_processor.markets_to_dataframe(data)

    def fetch_ticker(self, symbol: str, params: dict = {}) -> dict:
        data = self.exchange.fetch_ticker(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    def fetch_tickers(
        self, symbols: list[str] | None = None, params: dict = {}
    ) -> pd.DataFrame:
        data = self.exchange.fetch_tickers(symbols=symbols, params=params)
        return ccxt_processor.markets_to_dataframe(data)

    def fetch_order_book(
        self, symbol: str, limit: int | None = None, params: dict = {}
    ) -> pd.DataFrame:
        data = self.exchange.fetch_order_book(symbol=symbol, limit=limit, params=params)
        return ccxt_processor.order_book_to_dataframe(data)

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since=since,
            limit=limit,
            params=params,
        )
        return ccxt_processor.ohlcv_to_dataframe(data)

    def fetch_status(self, params: dict = {}) -> pd.DataFrame:
        data = self.exchange.fetch_status(params=params)
        return ccxt_processor.response_to_dataframe(data)

    def fetch_trades(
        self,
        symbol: str,
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_trades(
            symbol, since=since, limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_my_trades(
        self,
        symbol: str | None = None,
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_my_trades(
            symbol, since=since, limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_orders(
        self,
        symbol: str | None = None,
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_orders(
            symbol=symbol, since=since, limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    def fetch_open_orders(
        self,
        symbol: str | None = None,
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_open_orders(
            symbol=symbol, since=since, limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    def fetch_closed_orders(
        self,
        symbol: str | None = None,
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_closed_orders(
            symbol=symbol, since=since, limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    def fetch_order(
        self, id: str, symbol: str | None = None, params: dict = {}
    ) -> dict:
        data = self.exchange.fetch_order(id=id, symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    def create_order(
        self,
        symbol: str,
        type: Literal["limit", "market"],
        side: Literal["buy", "sell"],
        amount: float,
        price: float | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.create_order(
            symbol=symbol,
            type=type,
            side=side,
            amount=amount,
            price=price,
            params=params,
        )
        return ccxt_processor.orders_to_dataframe(data)

    def cancel_order(
        self, id: str, symbol: str | None = None, params: dict = {}
    ) -> pd.DataFrame:
        data = self.exchange.cancel_order(id, symbol=symbol, params=params)
        return ccxt_processor.orders_to_dataframe(data)
