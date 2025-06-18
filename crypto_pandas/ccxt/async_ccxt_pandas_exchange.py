import asyncio
import sys
from functools import wraps
from typing import Literal, Callable, Union

import ccxt.pro as ccxt
import pandas as pd
from dataclasses import dataclass, field

from async_lru import alru_cache

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
)
from crypto_pandas.utils.pandas_utils import (
    timestamp_to_int,
    preprocess_order,
    preprocess_order_dataframe,
)

ccxt_processor = BaseProcessor()
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@dataclass
class AsyncCCXTPandasExchange:
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

        async def preprocess_kwargs(kwargs: dict) -> dict:
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
                    markets=await self.load_cached_markets(),
                    max_notional=self.max_order_notional,
                    price_strategy=self.order_price_rounding,
                    amount_strategy=self.order_amount_rounding,
                )
                if "notional" in kwargs:
                    kwargs.pop("notional")
            elif method_name in bulk_order_methods:
                kwargs["orders"] = preprocess_order_dataframe(
                    orders=kwargs["orders"],
                    markets=await self.load_cached_markets(),
                    max_orders=self.max_number_of_orders,
                    max_notional=self.max_order_notional,
                    price_strategy=self.order_price_rounding,
                    amount_strategy=self.order_amount_rounding,
                )
                kwargs["orders"] = ccxt_processor.orders_to_dict(kwargs["orders"])
            elif method_name in symbol_order_methods:
                kwargs["orders"] = kwargs["orders"][["id", "symbol"]].to_dict("records")
            return kwargs

        def preprocess_data(result: dict | list) -> dict | list | pd.DataFrame:
            if method_name in standard_dataframe_methods:
                result = ccxt_processor.response_to_dataframe(result)
            elif method_name in markets_dataframe_methods:
                result = ccxt_processor.markets_to_dataframe(result)
            elif method_name in balance_dataframe_methods:
                result = ccxt_processor.balance_to_dataframe(result)
            elif method_name in ohlcv_dataframe_methods:
                result = ccxt_processor.ohlcv_to_dataframe(result)
            elif method_name in orderbook_dataframe_methods:
                result = ccxt_processor.order_book_to_dataframe(result)
            elif method_name in orders_dataframe_methods:
                result = ccxt_processor.orders_to_dataframe(result)
            elif method_name in dict_methods:
                result = ccxt_processor.preprocess_dict(result)
            return result

        @wraps(original_method)
        async def wrapped(*args, **kwargs) -> Union[dict, pd.DataFrame, asyncio.Future]:
            kwargs = await preprocess_kwargs(kwargs=kwargs)
            if asyncio.iscoroutinefunction(original_method):
                result = await original_method(*args, **kwargs)
                return preprocess_data(result)
            else:
                result = original_method(*args, **kwargs)
                return preprocess_data(result)

        return wrapped

    async def load_cached_markets(self, params: dict = {}) -> pd.DataFrame:

        @alru_cache(ttl=self.markets_cache_time)
        async def _cached_load_markets() -> pd.DataFrame:
            return await self.load_markets(reload=True, params=params)

        return await _cached_load_markets()
