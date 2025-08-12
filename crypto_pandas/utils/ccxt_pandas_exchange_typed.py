from decimal import Decimal
from types import NoneType
from typing import List, Union, Protocol
from ccxt.base.types import Int, OrderSide, OrderType, Str, Strings
import pandas as pd


class CCXTPandasExchangeTyped(Protocol):
    """A Class to add type hinting to CCXTPandasExchangeTyped"""

    def cancel_orders_for_symbols(self, orders: pd.DataFrame, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.cancel_orders_for_symbols"""
        ...

    def fetch_funding_history(self, symbol: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_funding_history"""
        ...

    def fetch_deposit_withdraw_fees(self, codes: Strings = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_deposit_withdraw_fees"""
        ...

    def fetch_trading_fee(self, symbol: str, params = {}) -> dict:
        """Returns a dict from ccxt.fetch_trading_fee"""
        ...

    def fetch_option_chain(self, code: str, params = {}) -> dict:
        """Returns a dict from ccxt.fetch_option_chain"""
        ...

    def watch_order_book(self, symbol: str, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.watch_order_book"""
        ...

    def fetch_my_liquidations(self, symbol: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_my_liquidations"""
        ...

    def watch_trades(self, symbol: str, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.watch_trades"""
        ...

    def fetch_ledger(self, code: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_ledger"""
        ...

    def fetch_deposits(self, code: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_deposits"""
        ...

    def fetch_leverage_tiers(self, symbols: Strings = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_leverage_tiers"""
        ...

    def watch_position(self, symbol: Str = None, params = {}) -> dict:
        """Returns a dict from ccxt.watch_position"""
        ...

    def fetch_markets(self, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_markets"""
        ...

    def fetch_last_prices(self, symbols: Strings = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_last_prices"""
        ...

    def fetch_mark_price(self, symbol: str, params = {}) -> dict:
        """Returns a dict from ccxt.fetch_mark_price"""
        ...

    def fetch_orders(self, symbol: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_orders"""
        ...

    def fetch_funding_rate(self, symbol: str, params = {}) -> dict:
        """Returns a dict from ccxt.fetch_funding_rate"""
        ...

    def watch_positions(self, symbols: Strings = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.watch_positions"""
        ...

    def fetch_transfers(self, code: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_transfers"""
        ...

    def fetch_greeks(self, symbol: str, params = {}) -> dict:
        """Returns a dict from ccxt.fetch_greeks"""
        ...

    def fetch_ticker(self, symbol: str, params = {}) -> dict:
        """Returns a dict from ccxt.fetch_ticker"""
        ...

    def watch_ohlcv(self, symbol: str, timeframe = '1m', since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.watch_ohlcv"""
        ...

    def create_orders(self, orders: pd.DataFrame, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.create_orders"""
        ...

    def fetch_order_trades(self, id: str, symbol: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_order_trades"""
        ...

    def fetch_withdrawals(self, code: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_withdrawals"""
        ...

    def fetch_currencies(self, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_currencies"""
        ...

    def fetch_order(self, id: str, symbol: Str = None, params = {}) -> dict:
        """Returns a dict from ccxt.fetch_order"""
        ...

    def fetch_position_history(self, symbol: str, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_position_history"""
        ...

    def fetch_isolated_borrow_rates(self, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_isolated_borrow_rates"""
        ...

    def watch_orders(self, symbol: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.watch_orders"""
        ...

    def edit_order(self, id: str, symbol: str, type: OrderType, side: OrderSide, amount: Union[NoneType, str, float, int, Decimal] = None, price: Union[NoneType, str, float, int, Decimal] = None, params = {}) -> dict:
        """Returns a dict from ccxt.edit_order"""
        ...

    def fetch_bids_asks(self, symbols: Strings = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_bids_asks"""
        ...

    def fetch_funding_rate_history(self, symbol: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_funding_rate_history"""
        ...

    def watch_liquidations_for_symbols(self, symbols: List[str], since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.watch_liquidations_for_symbols"""
        ...

    def edit_orders(self, orders: pd.DataFrame, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.edit_orders"""
        ...

    def watch_bids_asks(self, symbols: Strings = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.watch_bids_asks"""
        ...

    def watch_ohlcv_for_symbols(self, symbolsAndTimeframes: List[List[str]], since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.watch_ohlcv_for_symbols"""
        ...

    def fetch_balance(self, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_balance"""
        ...

    def fetch_closed_orders(self, symbol: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_closed_orders"""
        ...

    def fetch_all_greeks(self, symbols: Strings = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_all_greeks"""
        ...

    def watch_trades_for_symbols(self, symbols: List[str], since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.watch_trades_for_symbols"""
        ...

    def fetch_deposit_withdraw_fee(self, code: str, params = {}) -> dict:
        """Returns a dict from ccxt.fetch_deposit_withdraw_fee"""
        ...

    def fetch_position(self, symbol: str, params = {}) -> dict:
        """Returns a dict from ccxt.fetch_position"""
        ...

    def fetch_positions_history(self, symbols: Strings = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_positions_history"""
        ...

    def fetch_borrow_interest(self, code: Str = None, symbol: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_borrow_interest"""
        ...

    def fetch_my_trades(self, symbol: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_my_trades"""
        ...

    def fetch_order_book(self, symbol: str, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_order_book"""
        ...

    def fetch_canceled_and_closed_orders(self, symbol: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_canceled_and_closed_orders"""
        ...

    def fetch_convert_currencies(self, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_convert_currencies"""
        ...

    def fetch_tickers(self, symbols: Strings = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_tickers"""
        ...

    def fetch_positions_risk(self, symbols: Strings = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_positions_risk"""
        ...

    def fetch_status(self, params = {}) -> dict:
        """Returns a dict from ccxt.fetch_status"""
        ...

    def fetch_mark_prices(self, symbols: Strings = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_mark_prices"""
        ...

    def fetch_ohlcv(self, symbol: str, timeframe = '1m', since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_ohlcv"""
        ...

    def fetch_cross_borrow_rates(self, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_cross_borrow_rates"""
        ...

    def fetch_open_interest_history(self, symbol: str, timeframe = '1h', since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_open_interest_history"""
        ...

    def watch_order_book_for_symbols(self, symbols: List[str], limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.watch_order_book_for_symbols"""
        ...

    def fetch_positions(self, symbols: Strings = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_positions"""
        ...

    def watch_orders_for_symbols(self, symbols: List[str], since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.watch_orders_for_symbols"""
        ...

    def fetch_long_short_ratio_history(self, symbol: Str = None, timeframe: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_long_short_ratio_history"""
        ...

    def fetch_trades(self, symbol: str, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_trades"""
        ...

    def fetch_open_orders(self, symbol: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_open_orders"""
        ...

    def fetch_deposits_withdrawals(self, code: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_deposits_withdrawals"""
        ...

    def cancel_order(self, id: str, symbol: Str = None, params = {}) -> dict:
        """Returns a dict from ccxt.cancel_order"""
        ...

    def watch_my_trades(self, symbol: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.watch_my_trades"""
        ...

    def fetch_transaction_fees(self, codes: Strings = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_transaction_fees"""
        ...

    def watch_my_trades_for_symbols(self, symbols: List[str], since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.watch_my_trades_for_symbols"""
        ...

    def fetch_convert_trade_history(self, code: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_convert_trade_history"""
        ...

    def fetch_cross_borrow_rate(self, code: str, params = {}) -> dict:
        """Returns a dict from ccxt.fetch_cross_borrow_rate"""
        ...

    def fetch_margin_modes(self, symbols: Strings = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_margin_modes"""
        ...

    def watch_liquidations(self, symbol: str, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.watch_liquidations"""
        ...

    def fetch_open_interest(self, symbol: str, params = {}) -> dict:
        """Returns a dict from ccxt.fetch_open_interest"""
        ...

    def fetch_liquidations(self, symbol: str, since: int | pd.Timestamp | dict | str | None = None, limit: Int = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_liquidations"""
        ...

    def watch_ticker(self, symbol: str, params = {}) -> dict:
        """Returns a dict from ccxt.watch_ticker"""
        ...

    def fetch_funding_rates(self, symbols: Strings = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_funding_rates"""
        ...

    def fetch_margin_adjustment_history(self, symbol: Str = None, type: Str = None, since: int | pd.Timestamp | dict | str | None = None, limit: Union[NoneType, str, float, int, Decimal] = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_margin_adjustment_history"""
        ...

    def fetch_leverages(self, symbols: Strings = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_leverages"""
        ...

    def cancel_all_orders(self, symbol: Str = None, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.cancel_all_orders"""
        ...

    def load_markets(self, reload = False, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.load_markets"""
        ...

    def fetch_trading_fees(self, params = {}) -> pd.DataFrame:
        """Returns a pd.DataFrame from ccxt.fetch_trading_fees"""
        ...

    def fetch_option(self, symbol: str, params = {}) -> dict:
        """Returns a dict from ccxt.fetch_option"""
        ...

    def create_order(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Union[NoneType, str, float, int, Decimal] = None, params = {}) -> dict:
        """Returns a dict from ccxt.create_order"""
        ...

    def fetch_isolated_borrow_rate(self, symbol: str, params = {}) -> dict:
        """Returns a dict from ccxt.fetch_isolated_borrow_rate"""
        ...