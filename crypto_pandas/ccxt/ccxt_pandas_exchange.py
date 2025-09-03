from functools import wraps
from typing import Literal, Callable, Union
import ccxt
import pandas as pd
from dataclasses import dataclass, field

from cachetools.func import ttl_cache

from crypto_pandas.ccxt.base_processor import BaseProcessor
from crypto_pandas.ccxt.method_mappings import (
    bulk_order_methods,
    single_order_methods,
    symbol_order_methods,
    modified_methods,
)
from crypto_pandas.utils.ccxt_pandas_exchange_typed import CCXTPandasExchangeTyped
from crypto_pandas.utils.pandas_utils import (
    timestamp_to_int,
    preprocess_order,
    preprocess_order_dataframe,
)


@dataclass
class CCXTPandasExchange(CCXTPandasExchangeTyped):
    """
    CCXTPandasExchange is a wrapper for the CCXT library that integrates with Pandas
    to provide streamlined data processing for cryptocurrency exchanges. It enables users
    to seamlessly create orders, fetch market data, and process exchange responses as
    Pandas DataFrames.

    Attributes:
        exchange (ccxt.Exchange): An instance of the CCXT exchange client.
        exchange_name (str | None): The name of the exchange to interact with.
        account_name (str | None): The account name, if required for tracking.
        dropna_fields (bool): Determines whether empty (NaN) columns are removed from DataFrame outputs.
        max_order_cost (float): Maximum cost value for any single order.
        max_number_of_orders (int): Maximum number of bulk orders allowed.
        markets_cache_time (int): Cache duration (in seconds) for markets data.
        cost_out_of_range (str): Defines behavior when cost exceeds acceptable ranges. Options include:
            - "warn": Logs a warning while removing the order.
            - "clip": Clips or limits the volume to valid ranges.
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
    dropna_fields: bool = True
    max_order_cost: float = 10_000
    max_number_of_orders: int = 5
    markets_cache_time: int = 3600
    cost_out_of_range: Literal["warn", "clip"] = "warn"
    amount_out_of_range: Literal["warn", "clip"] = "warn"
    price_out_of_range: Literal["warn", "clip"] = "warn"
    _ccxt_processor: BaseProcessor = field(default_factory=BaseProcessor)

    def __post_init__(self):
        if self.exchange_name is None:
            self.exchange_name = self.exchange.id
        self._ccxt_processor = BaseProcessor(
            exchange_name=self.exchange_name,
            account_name=self.account_name,
            cost_out_of_range=self.cost_out_of_range,
            amount_out_of_range=self.amount_out_of_range,
            price_out_of_range=self.price_out_of_range,
        )

    def __getattribute__(self, method_name: str) -> Callable:
        if method_name not in modified_methods:
            return super().__getattribute__(method_name)
        original_method = getattr(self.exchange, method_name)

        @wraps(original_method)
        def wrapped(*args, **kwargs) -> Union[dict, pd.DataFrame]:
            if "since" in kwargs:
                kwargs["since"] = timestamp_to_int(kwargs["since"])
            if method_name in single_order_methods:
                kwargs["amount"], kwargs["price"] = preprocess_order(
                    exchange=self.exchange,
                    symbol=kwargs["symbol"],
                    order_type=kwargs["type"],
                    amount=kwargs.get("amount"),
                    price=kwargs.get("price"),
                    cost=kwargs.get("cost"),
                    markets=self.load_cached_markets(),
                    max_cost=self.max_order_cost,
                    cost_out_of_range=self.cost_out_of_range,
                    amount_out_of_range=self.amount_out_of_range,
                    price_out_of_range=self.price_out_of_range,
                )
                if "cost" in kwargs:
                    kwargs.pop("cost")
            elif method_name in bulk_order_methods:
                kwargs["orders"] = preprocess_order_dataframe(
                    orders=kwargs["orders"],
                    markets=self.load_cached_markets(),
                    max_orders=self.max_number_of_orders,
                    max_cost=self.max_order_cost,
                    cost_out_of_range=self.cost_out_of_range,
                    amount_out_of_range=self.amount_out_of_range,
                    price_out_of_range=self.price_out_of_range,
                )
                kwargs["orders"] = self._ccxt_processor.orders_to_dict(
                    orders=kwargs["orders"],
                    exchange=self.exchange,
                )
            elif method_name in symbol_order_methods:
                kwargs["orders"] = kwargs["orders"][["id", "symbol"]].to_dict("records")
            result = original_method(*args, **kwargs)
            result = self._ccxt_processor.preprocess_outputs(
                method_name=method_name, result=result, symbol=kwargs.get("symbol")
            )
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
