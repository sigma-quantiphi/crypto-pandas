import ccxt.pro as ccxt
import pandas as pd
from dataclasses import dataclass, field

from crypto_pandas.ccxt.base_processor import BaseProcessor
from crypto_pandas.utils.pandas_utils import timestamp_to_int

ccxt_processor = BaseProcessor()


@dataclass
class AsyncCCXTPandasExchange:
    exchange: ccxt.Exchange = field(default_factory=ccxt.binance)

    async def load_markets(
        self, reload: bool = False, params: dict = {}
    ) -> pd.DataFrame:
        data = await self.exchange.load_markets(reload=reload, params=params)
        return ccxt_processor.markets_to_dataframe(data)

    async def fetch_balance(self, params: dict = {}) -> pd.DataFrame:
        data = await self.exchange.fetch_balance(params=params)
        return ccxt_processor.balance_to_dataframe(data)

    async def fetch_positions_risk(
        self, symbols: list[str] | None = None, params: dict = {}
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_positions_risk(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_position(self, symbol: str, params: dict = {}) -> dict:
        data = await self.exchange.fetch_position(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    async def fetch_positions(
        self, symbols: list[str] | None = None, params: dict = {}
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_positions(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_transfers(
        self,
        code: str = None,
        since: int | pd.Timestamp | None = None,
        limit: int = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_transfers(
            code=code, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_ledger(
        self,
        code: str = None,
        since: int | pd.Timestamp | None = None,
        limit: int = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_ledger(
            code=code, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_withdrawals(
        self,
        symbol: str = None,
        since: int | pd.Timestamp | None = None,
        limit: int = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_withdrawals(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_currencies(self, params: dict = {}) -> pd.DataFrame:
        data = await self.exchange.fetch_currencies(params=params)
        return ccxt_processor.markets_to_dataframe(data)

    async def fetch_ticker(self, symbol: str, params: dict = {}) -> dict:
        data = await self.exchange.fetch_ticker(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    async def fetch_tickers(
        self, symbols: list[str] | None = None, params: dict = {}
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_tickers(symbols=symbols, params=params)
        return ccxt_processor.markets_to_dataframe(data)

    async def fetch_order_book(
        self, symbol: str, limit: int | None = None, params: dict = {}
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_order_book(
            symbol=symbol, limit=limit, params=params
        )
        return ccxt_processor.order_book_to_dataframe(data)

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since=timestamp_to_int(since),
            limit=limit,
            params=params,
        )
        return ccxt_processor.ohlcv_to_dataframe(data)

    async def fetch_funding_rate_history(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_funding_rate_history(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_open_interest(
        self,
        symbol: str,
        params: dict = {},
    ) -> dict:
        data = await self.exchange.fetch_open_interest(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    async def fetch_open_interest_history(
        self,
        symbol: str,
        timeframe: str = "1h",
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_open_interest_history(
            symbol=symbol,
            timeframe=timeframe,
            since=timestamp_to_int(since),
            limit=limit,
            params=params,
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_status(self, params: dict = {}) -> pd.DataFrame:
        data = await self.exchange.fetch_status(params=params)
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_trades(
        self,
        symbol: str,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_trades(
            symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_my_trades(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_my_trades(
            symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_leverages(
        self, symbols: list[str] | None = None, params: dict = {}
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_leverages(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_liquidations(
        self,
        symbol: str,
        since: int | pd.Timestamp | None = None,
        limit: int = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_liquidations(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_greeks(
        self,
        symbol: str | None = None,
        params: dict = {},
    ) -> dict:
        data = await self.exchange.fetch_greeks(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    async def fetch_long_short_ratio_history(
        self,
        symbol: str | None = None,
        timeframe: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_long_short_ratio_history(
            symbol=symbol,
            timeframe=timeframe,
            since=timestamp_to_int(since),
            limit=limit,
            params=params,
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_margin_adjustment_history(
        self,
        symbol: str | None = None,
        type: str | None = None,
        since: int | float | str | None = None,
        limit: int | float | str | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_margin_adjustment_history(
            symbol=symbol,
            type=type,
            since=timestamp_to_int(since),
            limit=limit,
            params=params,
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_my_liquidations(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_my_liquidations(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_option(
        self,
        symbol: str,
        params: dict = {},
    ) -> dict:
        data = await self.exchange.fetch_option(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    async def fetch_funding_rates(
        self,
        symbols: list[str] | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_funding_rates(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_convert_trade_history(
        self,
        code: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_convert_trade_history(
            code=code, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_bids_asks(
        self,
        symbols: list[str] | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_bids_asks(symbols=symbols, params=params)
        return ccxt_processor.markets_to_dataframe(data)

    async def fetch_orders(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_orders(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    async def fetch_open_orders(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_open_orders(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    async def fetch_closed_orders(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_closed_orders(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    async def fetch_canceled_and_closed_orders(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.fetch_canceled_and_closed_orders(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    async def fetch_order(
        self, id: str, symbol: str | None = None, params: dict = {}
    ) -> dict:
        data = await self.exchange.fetch_order(id=id, symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    async def watch_liquidations(
        self,
        symbol: str,
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """Real-time ticker stream via websocket"""
        data = await self.exchange.watch_liquidations(
            symbol=symbol, since=since, limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def watch_liquidations_for_symbols(
        self,
        symbols: list[str],
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """Real-time ticker stream via websocket"""
        data = await self.exchange.watch_liquidations_for_symbols(
            symbols=symbols, since=since, limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def watch_ticker(self, symbol: str, params: dict = {}) -> dict:
        """Real-time ticker stream via websocket"""
        data = await self.exchange.watch_ticker(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    async def watch_orders(
        self,
        symbol: str,
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        trades = await self.exchange.watch_orders(
            symbol=symbol, since=since, limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(trades)

    async def watch_orders_for_symbols(
        self,
        symbols: list[str],
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        trades = await self.exchange.watch_orders_for_symbols(
            symbols=symbols, since=since, limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(trades)

    async def watch_position(
        self,
        symbol: str,
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        trades = await self.exchange.watch_position(
            symbol=symbol, since=since, limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(trades)

    async def watch_positions(
        self,
        symbols: list[str],
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        trades = await self.exchange.watch_positions(
            symbols=symbols, since=since, limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(trades)

    async def watch_bids_asks(
        self, symbols: list[str], params: dict = {}
    ) -> pd.DataFrame:
        data = await self.exchange.watch_bids_asks(symbols=symbols, params=params)
        return ccxt_processor.markets_to_dataframe(data)

    async def watch_order_book(
        self, symbol: str, limit: int | None = None, params: dict = {}
    ) -> pd.DataFrame:
        data = await self.exchange.watch_order_book(
            symbol=symbol, limit=limit, params=params
        )
        return ccxt_processor.order_book_to_dataframe(data)

    async def watch_order_book_for_symbols(
        self, symbols: list[str], limit: int | None = None, params: dict = {}
    ) -> pd.DataFrame:
        data = await self.exchange.watch_order_book_for_symbols(
            symbols=symbols, limit=limit, params=params
        )
        return ccxt_processor.order_book_to_dataframe(data)

    async def watch_my_trades(
        self,
        symbol: str,
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        trades = await self.exchange.watch_my_trades(
            symbol=symbol, since=since, limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(trades)

    async def watch_my_trades_for_symbols(
        self,
        symbols: list[str],
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        trades = await self.exchange.watch_my_trades_for_symbols(
            symbols=symbols, since=since, limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(trades)

    async def watch_trades(
        self,
        symbol: str,
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        trades = await self.exchange.watch_trades(
            symbol=symbol, since=since, limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(trades)

    async def watch_trades_for_symbols(
        self,
        symbols: list[str],
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        trades = await self.exchange.watch_trades_for_symbols(
            symbols=symbols, since=since, limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(trades)

    async def watch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.watch_ohlcv(
            symbol=symbol, timeframe=timeframe, since=since, limit=limit, params=params
        )
        return ccxt_processor.ohlcv_to_dataframe(data)

    async def watch_ohlcv_for_symbols(
        self,
        symbolsAndTimeframes: list[list[str]],
        since: int | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = await self.exchange.watch_ohlcv_for_symbols(
            symbolsAndTimeframes=symbolsAndTimeframes,
            since=since,
            limit=limit,
            params=params,
        )
        return ccxt_processor.ohlcv_to_dataframe(data)

    async def close(self):
        """Close websocket connections"""
        await self.exchange.close()
