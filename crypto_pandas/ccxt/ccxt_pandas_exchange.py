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
    orderbooks_dataframe_methods,
)
from crypto_pandas.utils.pandas_utils import (
    timestamp_to_int,
    preprocess_order,
    preprocess_order_dataframe,
)


@dataclass
class CCXTPandasExchange:
    """
    CCXTPandasExchange is a wrapper for the CCXT library that integrates with Pandas
    to provide streamlined data processing for cryptocurrency exchanges. It enables users
    to seamlessly create orders, fetch market data, and process exchange responses as
    Pandas DataFrames.

    Attributes:
        exchange (ccxt.Exchange): An instance of the CCXT exchange client.
        exchange_name (str | None): The name of the exchange to interact with.
        account_name (str | None): The account name, if required for tracking.
        max_order_notional (float): Maximum notional value for any single order.
        max_number_of_orders (int): Maximum number of bulk orders allowed.
        markets_cache_time (int): Cache duration (in seconds) for markets data.
        order_amount_rounding (Literal["floor", "ceil", "round"]): Strategy for rounding order amounts.
        order_price_rounding (Literal["aggressive", "defensive", "round"]): Strategy for rounding order prices.
        amount_out_of_range (str): Defines behavior when volume exceeds acceptable ranges. Options include:
            - "warn": Logs a warning while removing the order.
            - "clip": Clips or limits the volume to valid ranges.
        price_out_of_range (str): Defines behavior when price exceeds allowable ranges. Options include:
            - "warn": Logs a warning while removing the order.
            - "clip": Adjusts the price to fit within predefined limits.
        _ccxt_processor (BaseProcessor): A helper class to process CCXT responses and provide consistent output.

    Methods:
        __getattr__(method_name: str): Overridden to enable dynamic method resolution for CCXT methods,
                                       with transformations applied to handle inputs and outputs as Pandas DataFrames.
        load_cached_markets(params: dict = {}): Loads and caches market data from the exchange.
    """

    exchange: ccxt.Exchange = field(default_factory=ccxt.binance)
    exchange_name: str | None = None
    account_name: str | None = None
    max_order_notional: float = 10_000
    max_number_of_orders: int = 5
    markets_cache_time: int = 3600
    order_amount_rounding: Literal["floor", "ceil", "round"] = "round"
    order_price_rounding: Literal["aggressive", "defensive", "round"] = "round"
    amount_out_of_range: Literal["warn", "clip"] = "warn"
    price_out_of_range: Literal["warn", "clip"] = "warn"
    _ccxt_processor: BaseProcessor = field(default_factory=BaseProcessor)

    def __post_init__(self):
        self._ccxt_processor = BaseProcessor(
            exchange_name=self.exchange_name,
            account_name=self.account_name,
            amount_out_of_range=self.amount_out_of_range,
            price_out_of_range=self.price_out_of_range,
        )

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
                kwargs["orders"] = self._ccxt_processor.orders_to_dict(
                    orders=kwargs["orders"]
                )
            elif method_name in symbol_order_methods:
                kwargs["orders"] = kwargs["orders"][["id", "symbol"]].to_dict("records")
            result = original_method(*args, **kwargs)
            if method_name in standard_dataframe_methods:
                result = self._ccxt_processor.response_to_dataframe(data=result)
            elif method_name in markets_dataframe_methods:
                result = self._ccxt_processor.markets_to_dataframe(data=result)
            elif method_name in balance_dataframe_methods:
                result = self._ccxt_processor.balance_to_dataframe(data=result)
            elif method_name in ohlcv_dataframe_methods:
                result = self._ccxt_processor.ohlcv_to_dataframe(
                    data=result, symbol=kwargs.get("symbol")
                )
            elif method_name in orderbook_dataframe_methods:
                result = self._ccxt_processor.order_book_to_dataframe(data=result)
            elif method_name in orderbooks_dataframe_methods:
                result = self._ccxt_processor.order_books_to_dataframe(data=result)
            elif method_name in orders_dataframe_methods:
                result = self._ccxt_processor.orders_to_dataframe(data=result)
            elif method_name in ohlcv_symbols_dataframe_methods:
                result = self._ccxt_processor.ohlcv_symbols_to_dataframe(data=result)
            elif method_name in dict_methods:
                result = self._ccxt_processor.preprocess_dict(data=result)
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
