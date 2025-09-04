import asyncio
import sys
from functools import wraps
from typing import Literal, Callable, Union
from asyncio import Semaphore

import ccxt.pro as ccxt
import pandas as pd
from dataclasses import dataclass, field

from async_lru import alru_cache

from crypto_pandas.ccxt.base_processor import BaseProcessor
from crypto_pandas.ccxt.method_mappings import (
    bulk_order_methods,
    single_order_methods,
    symbol_order_methods,
    modified_methods,
)
from crypto_pandas.utils.async_ccxt_pandas_exchange_typed import (
    AsyncCCXTPandasExchangeTyped,
)
from crypto_pandas.utils.pandas_utils import (
    timestamp_to_int,
    preprocess_order,
    preprocess_order_dataframe,
)
from crypto_pandas.utils.utils import exchange_has_method

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@dataclass
class AsyncCCXTPandasExchange(AsyncCCXTPandasExchangeTyped):
    """
    An asynchronous wrapper class for ccxt Exchange that integrates pandas for enhanced data handling
    and provides preprocessing utilities for working with cryptocurrency trading data.

    Attributes:
        exchange (ccxt.Exchange): The ccxt exchange instance, defaulting to Binance.
        exchange_name (str | None): The name of the exchange, used for processor initialization.
        account_name (str | None): The account name, used for processor initialization.
        dropna_fields (bool): Determines whether empty (NaN) columns are removed from DataFrame outputs.
        max_order_cost (float): The maximum allowable cost value for a single order.
        max_number_of_orders (int): The maximum number of orders allowed in bulk order processing.
        markets_cache_time (int): The cache time in seconds for market data.
        cost_out_of_range (str): Defines behavior when cost exceeds acceptable ranges. Options include:
            - "warn": Logs a warning while removing the order.
            - "clip": Clips or limits the volume to valid ranges.
        amount_out_of_range (str): Defines behavior when volume exceeds acceptable ranges. Options include:
            - "warn": Logs a warning while removing the order.
            - "clip": Clips or limits the volume to valid ranges.
        price_out_of_range (str): Defines behavior when price exceeds allowable ranges. Options include:
            - "warn": Logs a warning while removing the order.
            - "clip": Adjusts the price to fit within predefined limits.
        semaphore_value (int): The value for the asyncio Semaphore controlling concurrent requests.
        _ccxt_processor (BaseProcessor): The processor handling preprocessing tasks for ccxt methods.
        _semaphore (Semaphore): An asyncio Semaphore instance to limit concurrency.

    Methods:
        __getattr__(method_name: str) -> Callable:
            Dynamically intercepts ccxt methods to preprocess inputs/outputs and adds semaphore control.

        load_cached_markets(params: dict = {}) -> pd.DataFrame:
            Loads and caches markets data asynchronously, with optional parameters for customization.
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
    semaphore_value: int = 1000
    _ccxt_processor: BaseProcessor = field(default_factory=BaseProcessor)
    _semaphore: Semaphore = field(default_factory=Semaphore)

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
        self._semaphore = Semaphore(self.semaphore_value)

    def __getattribute__(self, method_name: str) -> Callable:
        if method_name not in modified_methods | {"close"}:
            return super().__getattribute__(method_name)
        original_method = getattr(self.exchange, method_name)

        async def preprocess_kwargs(kwargs: dict) -> dict:
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
                    markets=await self.load_cached_markets(),
                    max_cost=self.max_order_cost,
                    price_out_of_range=self.price_out_of_range,
                    amount_out_of_range=self.amount_out_of_range,
                )
                if "cost" in kwargs:
                    kwargs.pop("cost")
            elif method_name in bulk_order_methods:
                kwargs["orders"] = preprocess_order_dataframe(
                    orders=kwargs["orders"],
                    markets=await self.load_cached_markets(),
                    max_orders=self.max_number_of_orders,
                    max_cost=self.max_order_cost,
                    price_out_of_range=self.price_out_of_range,
                    amount_out_of_range=self.amount_out_of_range,
                )
                kwargs["orders"] = self._ccxt_processor.orders_to_dict(
                    kwargs["orders"], exchange=self.exchange
                )
            elif method_name in symbol_order_methods:
                kwargs["orders"] = kwargs["orders"][["id", "symbol"]].to_dict("records")
            return kwargs

        @wraps(original_method)
        async def wrapped(*args, **kwargs) -> Union[dict, pd.DataFrame, asyncio.Future]:
            kwargs = await preprocess_kwargs(kwargs=kwargs)
            async with self._semaphore:
                if asyncio.iscoroutinefunction(original_method):
                    result = await original_method(*args, **kwargs)
                    return self._ccxt_processor.preprocess_outputs(
                        method_name=method_name,
                        result=result,
                        symbol=kwargs.get("symbol"),
                    )
                else:
                    result = original_method(*args, **kwargs)
                    return self._ccxt_processor.preprocess_outputs(
                        method_name=method_name,
                        result=result,
                        symbol=kwargs.get("symbol"),
                    )

        return wrapped

    async def load_cached_markets(self, params: dict = {}) -> pd.DataFrame:

        @alru_cache(ttl=self.markets_cache_time)
        async def _cached_load_markets() -> pd.DataFrame:
            async with self._semaphore:
                return await self.load_markets(reload=True, params=params)

        return await _cached_load_markets()

    def has_method(self, method_name: str) -> bool:
        return exchange_has_method(self.exchange, method_name)