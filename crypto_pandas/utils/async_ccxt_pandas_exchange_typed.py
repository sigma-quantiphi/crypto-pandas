from decimal import Decimal
from types import NoneType
from typing import List, Union, Awaitable
from ccxt.base.types import Int, OrderSide, OrderType, Str, Strings
import pandas as pd


class AsyncCCXTPandasExchangeTyped:
    """A Class to add type hinting to AsyncCCXTPandasExchangeTyped"""

    async def fetch_tickers(
        self, symbols: Strings = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_tickers"""
        ...

    async def edit_order(
        self,
        id: str,
        symbol: str,
        type: OrderType,
        side: OrderSide,
        amount: Union[NoneType, str, float, int, Decimal] = None,
        price: Union[NoneType, str, float, int, Decimal] = None,
        params={},
    ) -> Awaitable[dict]:
        """Returns a dict from ccxt.edit_order"""
        ...

    async def fetch_currencies(self, params={}) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_currencies"""
        ...

    async def fetch_option(self, symbol: str, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.fetch_option"""
        ...

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe="1m",
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_ohlcv"""
        ...

    async def cancel_orders_for_symbols(
        self, orders: pd.DataFrame, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.cancel_orders_for_symbols"""
        ...

    async def fetch_canceled_and_closed_orders(
        self,
        symbol: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_canceled_and_closed_orders"""
        ...

    async def fetch_deposits_withdrawals(
        self,
        code: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_deposits_withdrawals"""
        ...

    async def watch_position(self, symbol: Str = None, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.watch_position"""
        ...

    async def fetch_cross_borrow_rate(self, code: str, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.fetch_cross_borrow_rate"""
        ...

    async def fetch_option_chain(self, code: str, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.fetch_option_chain"""
        ...

    async def fetch_position(self, symbol: str, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.fetch_position"""
        ...

    async def watch_positions(
        self,
        symbols: Strings = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.watch_positions"""
        ...

    async def fetch_funding_rates(
        self, symbols: Strings = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_funding_rates"""
        ...

    async def fetch_funding_rate_history(
        self,
        symbol: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_funding_rate_history"""
        ...

    async def watch_bids_asks(
        self, symbols: Strings = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.watch_bids_asks"""
        ...

    async def fetch_margin_modes(
        self, symbols: Strings = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_margin_modes"""
        ...

    async def watch_trades_for_symbols(
        self,
        symbols: List[str],
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.watch_trades_for_symbols"""
        ...

    async def fetch_my_trades(
        self,
        symbol: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_my_trades"""
        ...

    async def fetch_convert_trade_history(
        self,
        code: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_convert_trade_history"""
        ...

    async def fetch_open_interest(self, symbol: str, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.fetch_open_interest"""
        ...

    async def watch_ticker(self, symbol: str, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.watch_ticker"""
        ...

    async def fetch_position_history(
        self,
        symbol: str,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_position_history"""
        ...

    async def fetch_borrow_interest(
        self,
        code: Str = None,
        symbol: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_borrow_interest"""
        ...

    async def fetch_positions_history(
        self,
        symbols: Strings = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_positions_history"""
        ...

    async def fetch_funding_history(
        self,
        symbol: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_funding_history"""
        ...

    async def fetch_orders(
        self,
        symbol: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_orders"""
        ...

    async def fetch_deposit_withdraw_fees(
        self, codes: Strings = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_deposit_withdraw_fees"""
        ...

    async def edit_orders(self, orders: pd.DataFrame, params={}) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.edit_orders"""
        ...

    async def create_order(
        self,
        symbol: str,
        type: OrderType,
        side: OrderSide,
        amount: float,
        price: Union[NoneType, str, float, int, Decimal] = None,
        params={},
    ) -> Awaitable[dict]:
        """Returns a dict from ccxt.create_order"""
        ...

    async def cancel_order(self, id: str, symbol: Str = None, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.cancel_order"""
        ...

    async def fetch_mark_prices(
        self, symbols: Strings = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_mark_prices"""
        ...

    async def watch_liquidations(
        self,
        symbol: str,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.watch_liquidations"""
        ...

    async def fetch_order_book(
        self, symbol: str, limit: Int = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_order_book"""
        ...

    async def watch_orders(
        self,
        symbol: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.watch_orders"""
        ...

    async def fetch_positions_risk(
        self, symbols: Strings = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_positions_risk"""
        ...

    async def fetch_ticker(self, symbol: str, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.fetch_ticker"""
        ...

    async def fetch_closed_orders(
        self,
        symbol: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_closed_orders"""
        ...

    async def fetch_status(self, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.fetch_status"""
        ...

    async def watch_trades(
        self,
        symbol: str,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.watch_trades"""
        ...

    async def fetch_my_liquidations(
        self,
        symbol: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_my_liquidations"""
        ...

    async def fetch_isolated_borrow_rate(self, symbol: str, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.fetch_isolated_borrow_rate"""
        ...

    async def fetch_markets(self, params={}) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_markets"""
        ...

    async def fetch_all_greeks(
        self, symbols: Strings = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_all_greeks"""
        ...

    async def fetch_withdrawals(
        self,
        code: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_withdrawals"""
        ...

    async def fetch_funding_rate(self, symbol: str, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.fetch_funding_rate"""
        ...

    async def fetch_leverages(
        self, symbols: Strings = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_leverages"""
        ...

    async def fetch_liquidations(
        self,
        symbol: str,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_liquidations"""
        ...

    async def fetch_margin_adjustment_history(
        self,
        symbol: Str = None,
        type: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Union[NoneType, str, float, int, Decimal] = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_margin_adjustment_history"""
        ...

    async def fetch_cross_borrow_rates(self, params={}) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_cross_borrow_rates"""
        ...

    async def fetch_deposit_withdraw_fee(self, code: str, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.fetch_deposit_withdraw_fee"""
        ...

    async def fetch_long_short_ratio_history(
        self,
        symbol: Str = None,
        timeframe: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_long_short_ratio_history"""
        ...

    async def load_markets(self, reload=False, params={}) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.load_markets"""
        ...

    async def watch_ohlcv_for_symbols(
        self,
        symbolsAndTimeframes: List[List[str]],
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.watch_ohlcv_for_symbols"""
        ...

    async def fetch_order(self, id: str, symbol: Str = None, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.fetch_order"""
        ...

    async def fetch_greeks(self, symbol: str, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.fetch_greeks"""
        ...

    async def fetch_ledger(
        self,
        code: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_ledger"""
        ...

    async def fetch_trades(
        self,
        symbol: str,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_trades"""
        ...

    async def fetch_leverage_tiers(
        self, symbols: Strings = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_leverage_tiers"""
        ...

    async def fetch_convert_currencies(self, params={}) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_convert_currencies"""
        ...

    async def fetch_trading_fees(self, params={}) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_trading_fees"""
        ...

    async def watch_order_book_for_symbols(
        self, symbols: List[str], limit: Int = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.watch_order_book_for_symbols"""
        ...

    async def fetch_mark_price(self, symbol: str, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.fetch_mark_price"""
        ...

    async def watch_liquidations_for_symbols(
        self,
        symbols: List[str],
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.watch_liquidations_for_symbols"""
        ...

    async def watch_my_trades_for_symbols(
        self,
        symbols: List[str],
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.watch_my_trades_for_symbols"""
        ...

    async def watch_order_book(
        self, symbol: str, limit: Int = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.watch_order_book"""
        ...

    async def fetch_transaction_fees(
        self, codes: Strings = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_transaction_fees"""
        ...

    async def fetch_open_interest_history(
        self,
        symbol: str,
        timeframe="1h",
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_open_interest_history"""
        ...

    async def fetch_trading_fee(self, symbol: str, params={}) -> Awaitable[dict]:
        """Returns a dict from ccxt.fetch_trading_fee"""
        ...

    async def fetch_deposits(
        self,
        code: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_deposits"""
        ...

    async def fetch_positions(
        self, symbols: Strings = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_positions"""
        ...

    async def fetch_balance(self, params={}) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_balance"""
        ...

    async def watch_ohlcv(
        self,
        symbol: str,
        timeframe="1m",
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.watch_ohlcv"""
        ...

    async def create_orders(self, orders: pd.DataFrame, params={}) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.create_orders"""
        ...

    async def cancel_all_orders(
        self, symbol: Str = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.cancel_all_orders"""
        ...

    async def fetch_bids_asks(
        self, symbols: Strings = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_bids_asks"""
        ...

    async def fetch_order_trades(
        self,
        id: str,
        symbol: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_order_trades"""
        ...

    async def watch_my_trades(
        self,
        symbol: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.watch_my_trades"""
        ...

    async def fetch_open_orders(
        self,
        symbol: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_open_orders"""
        ...

    async def fetch_transfers(
        self,
        code: Str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_transfers"""
        ...

    async def fetch_last_prices(
        self, symbols: Strings = None, params={}
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_last_prices"""
        ...

    async def watch_orders_for_symbols(
        self,
        symbols: List[str],
        since: int | pd.Timestamp | dict | str | None = None,
        limit: Int = None,
        params={},
    ) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.watch_orders_for_symbols"""
        ...

    async def fetch_isolated_borrow_rates(self, params={}) -> Awaitable[pd.DataFrame]:
        """Returns a pd.DataFrame from ccxt.fetch_isolated_borrow_rates"""
        ...
