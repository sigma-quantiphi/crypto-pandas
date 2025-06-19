from functools import wraps
from typing import Literal, Callable, Union

import ccxt
import pandas as pd
from dataclasses import dataclass, field

from cachetools.func import ttl_cache

from crypto_pandas.ccxt.base_processor import BaseProcessor
from crypto_pandas.ccxt.method_mappings import (
    orderbook_dataframe_methods,
    orders_dataframe_methods,
    dict_methods,
    ohlcv_dataframe_methods,
    balance_dataframe_methods,
    markets_dataframe_methods,
    standard_dataframe_methods,
    bulk_order_methods,
    single_order_methods,
    symbol_order_methods,
    ohlcv_symbols_dataframe_methods,
)
from crypto_pandas.utils.pandas_utils import (
    timestamp_to_int,
    preprocess_order,
    preprocess_order_dataframe,
)

ccxt_processor = BaseProcessor()


@dataclass
class CCXTPandasExchange:
    """
    A wrapper class for a CCXT exchange with extended functionalities using pandas.

    This class extends the CCXT `Exchange` class and provides additional methods
    for working with cryptocurrency exchanges. It integrates with pandas DataFrames
    for processing and presenting exchange data as well as preprocessing and
    validation mechanisms for orders.

    Attributes:
        exchange (Exchange): Instance of a CCXT exchange, defaulting to Binance.
        max_order_notional (float): Upper limit for the total notional value of an order.
            Default is 10,000.
        max_number_of_orders (int): Maximum number of allowed orders in a batch.
            Default is 5.
        markets_cache_time (int): Time to cache market data in seconds. Default is 86400
            seconds (1 day).
        order_amount_rounding (Literal["floor", "ceil", "round"]): Strategy for rounding
            order amounts. Default is "round".
        order_price_rounding (Literal["aggressive", "defensive", "round"]): Strategy for
            rounding order prices. Default is "round".

        Methods:
        load_markets: Load market data and cache it.
        fetch_balance: Fetch account balance as a DataFrame.
        fetch_trading_fee: Fetch trading fee as a DataFrame.
        fetch_trading_fees: Fetch trading fees as a DataFrame.
        fetch_positions_risk: Fetch risk information for open positions.
        fetch_position: Fetch details of a specific position.
        fetch_positions: Fetch all positions.
        fetch_transfers: Fetch transfer history.
        fetch_ledger: Fetch the account ledger.
        fetch_withdrawals: Fetch withdrawal history.
        fetch_currencies: Fetch supported currencies.
        fetch_ticker: Fetch ticker information for a specific symbol.
        fetch_tickers: Fetch all tickers as a DataFrame.
        fetch_order_book: Fetch order book for a given symbol.
        fetch_ohlcv: Fetch OHLCV (candlestick) data.
        fetch_funding_history: Fetch historical funding data.
        fetch_funding_rate_history: Fetch historical funding rates.
        fetch_open_interest: Fetch open interest for a given symbol.
        fetch_open_interest_history: Fetch historical open interest.
        fetch_status: Fetch the exchange status.
        fetch_trades: Fetch recent trades for a given symbol.
        fetch_my_trades: Fetch user's trade history.
        fetch_leverages: Fetch leverage settings.
        fetch_liquidations: Fetch liquidation events.
        fetch_greeks: Fetch greek values (options metrics).
        fetch_long_short_ratio_history: Fetch historical long-short ratios.
        fetch_margin_adjustment_history: Fetch historical margin adjustment data.
        fetch_my_liquidations: Fetch user's liquidation history.
        fetch_option: Fetch option details.
        fetch_funding_rates: Fetch funding rates.
        fetch_convert_trade_history: Fetch historical convert trades.
        fetch_bids_asks: Fetch the latest bid/ask prices for multiple symbols.
        fetch_orders: Fetch order history.
        fetch_open_orders: Fetch open orders.
        fetch_closed_orders: Fetch closed orders.
        fetch_canceled_and_closed_orders: Fetch canceled and closed orders.
        fetch_order: Fetch details of a specific order.
        create_order: Create a new order after preprocessing.
        cancel_order: Cancel a given order by ID.
        edit_order: Edit an existing order with new parameters.
        create_orders: Batch-create multiple orders.
        cancel_orders: Cancel a batch of orders using their IDs.
        cancel_all_orders: Cancel all orders for a specific symbol or account-wide.
        cancel_orders_for_symbols: Cancel specific orders across symbols.
        edit_orders: Batch-edit multiple orders.

    """

    exchange: ccxt.Exchange = field(default_factory=ccxt.binance)
    max_order_notional: float = 10_000
    max_number_of_orders: int = 5
    markets_cache_time: int = 3600
    order_amount_rounding: Literal["floor", "ceil", "round"] = "round"
    order_price_rounding: Literal["aggressive", "defensive", "round"] = "round"

    def __getattr__(self, method_name: str) -> Callable:
        original_method = getattr(self.exchange, method_name)
        if not callable(original_method):
            return original_method

        @wraps(original_method)
        def wrapped(*args, **kwargs) -> Union[dict, pd.DataFrame]:
            if "since" in kwargs:
                kwargs["since"] = timestamp_to_int(kwargs["since"])
            if method_name in single_order_methods:
                kwargs["amount"], kwargs["price"] = preprocess_order(
                    symbol=kwargs["symbol"],
                    type=kwargs["type"],
                    side=kwargs["side"],
                    amount=kwargs.get("amount"),
                    price=kwargs.get("price"),
                    notional=kwargs.get("notional"),
                    markets=self.load_cached_markets(),
                    max_notional=self.max_order_notional,
                    price_strategy=self.order_price_rounding,
                    amount_strategy=self.order_amount_rounding,
                )
                if "notional" in kwargs:
                    kwargs.pop("notional")
            elif method_name in bulk_order_methods:
                kwargs["orders"] = preprocess_order_dataframe(
                    orders=kwargs["orders"],
                    markets=self.load_cached_markets(),
                    max_orders=self.max_number_of_orders,
                    max_notional=self.max_order_notional,
                    price_strategy=self.order_price_rounding,
                    amount_strategy=self.order_amount_rounding,
                )
                kwargs["orders"] = ccxt_processor.orders_to_dict(
                    orders=kwargs["orders"]
                )
            elif method_name in symbol_order_methods:
                kwargs["orders"] = kwargs["orders"][["id", "symbol"]].to_dict("records")
            result = original_method(*args, **kwargs)
            if method_name in standard_dataframe_methods:
                result = ccxt_processor.response_to_dataframe(data=result)
            elif method_name in markets_dataframe_methods:
                result = ccxt_processor.markets_to_dataframe(data=result)
            elif method_name in balance_dataframe_methods:
                result = ccxt_processor.balance_to_dataframe(data=result)
            elif method_name in ohlcv_dataframe_methods:
                result = ccxt_processor.ohlcv_to_dataframe(
                    data=result, symbol=kwargs.get("symbol")
                )
            elif method_name in orderbook_dataframe_methods:
                result = ccxt_processor.order_book_to_dataframe(data=result)
            elif method_name in orders_dataframe_methods:
                result = ccxt_processor.orders_to_dataframe(data=result)
            elif method_name in ohlcv_symbols_dataframe_methods:
                result = ccxt_processor.ohlcv_symbols_to_dataframe(data=result)
            elif method_name in dict_methods:
                result = ccxt_processor.preprocess_dict(data=result)
            return result

        return wrapped

    def load_cached_markets(self, params: dict = {}) -> pd.DataFrame:
        """
        Loads market data from the exchange and caches it.

        Args:
            params (dict, optional): Additional parameters for the exchange's market-loading function.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A DataFrame containing the market data.
        """

        @ttl_cache(ttl=self.markets_cache_time)
        def _cached_load_markets() -> pd.DataFrame:
            return self.load_markets(reload=True, params=params)

        return _cached_load_markets()
