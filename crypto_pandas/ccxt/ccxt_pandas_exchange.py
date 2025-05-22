from functools import wraps
from typing import Literal

import ccxt
import numpy as np
import pandas as pd
from dataclasses import dataclass, field

from cachetools.func import ttl_cache
from ccxt import Exchange

from crypto_pandas.ccxt.base_processor import BaseProcessor
from crypto_pandas.utils.pandas_utils import (
    timestamp_to_int,
    date_time_columns_to_int_str,
    combine_params,
)

ccxt_processor = BaseProcessor()
order_data_columns = [
    "symbol",
    "precision_amount",
    "precision_price",
    "limits_price.min",
    "limits_price.max",
    "limits_amount.min",
    "limits_amount.max",
]


@dataclass
class CCXTPandasExchange(Exchange):
    exchange: Exchange = field(default_factory=ccxt.binance)
    max_order_notional: float = 10_000
    max_number_of_orders: int = 5
    markets_cache_time: int = 86400
    order_amount_rounding: Literal["floor", "ceil", "round"] = "round"
    order_price_rounding: Literal["aggressive", "defensive", "round"] = "round"

    def load_markets(self, reload: bool = False, params: dict = {}) -> pd.DataFrame:
        @ttl_cache(ttl=self.markets_cache_time)
        def _cached_load_markets():
            return self.exchange.load_markets(reload=reload, params=params)

        data = _cached_load_markets()
        return ccxt_processor.markets_to_dataframe(data)

    def fetch_balance(self, params: dict = {}) -> pd.DataFrame:
        data = self.exchange.fetch_balance(params=params)
        return ccxt_processor.balance_to_dataframe(data)

    def fetch_position(self, symbol: str, params: dict = {}) -> dict:
        data = self.exchange.fetch_position(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    def fetch_positions(
        self, symbols: list[str] | None = None, params: dict = {}
    ) -> pd.DataFrame:
        data = self.exchange.fetch_positions(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    def fetch_transfers(
        self,
        code: str = None,
        since: int | pd.Timestamp | None = None,
        limit: int = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_transfers(
            code=code, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_ledger(
        self,
        code: str = None,
        since: int | pd.Timestamp | None = None,
        limit: int = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_ledger(
            code=code, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_withdrawals(
        self,
        symbol: str = None,
        since: int | pd.Timestamp | None = None,
        limit: int = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_withdrawals(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

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
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since=timestamp_to_int(since),
            limit=limit,
            params=params,
        )
        return ccxt_processor.ohlcv_to_dataframe(data)

    def fetch_funding_rate_history(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_funding_rate_history(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_open_interest(
        self,
        symbol: str,
        params: dict = {},
    ) -> dict:
        data = self.exchange.fetch_open_interest(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    def fetch_open_interest_history(
        self,
        symbol: str,
        timeframe: str = "1h",
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_open_interest_history(
            symbol=symbol,
            timeframe=timeframe,
            since=timestamp_to_int(since),
            limit=limit,
            params=params,
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_status(self, params: dict = {}) -> pd.DataFrame:
        data = self.exchange.fetch_status(params=params)
        return ccxt_processor.response_to_dataframe(data)

    def fetch_trades(
        self,
        symbol: str,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_trades(
            symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_my_trades(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_my_trades(
            symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_leverages(
        self, symbols: list[str] | None = None, params: dict = {}
    ) -> pd.DataFrame:
        data = self.exchange.fetch_leverages(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    def fetch_liquidations(
        self,
        symbol: str,
        since: int | pd.Timestamp | None = None,
        limit: int = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_liquidations(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_greeks(
        self,
        symbol: str | None = None,
        params: dict = {},
    ) -> dict:
        data = self.exchange.fetch_greeks(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    def fetch_long_short_ratio_history(
        self,
        symbol: str | None = None,
        timeframe: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_long_short_ratio_history(
            symbol=symbol,
            timeframe=timeframe,
            since=timestamp_to_int(since),
            limit=limit,
            params=params,
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_margin_adjustment_history(
        self,
        symbol: str | None = None,
        type: str | None = None,
        since: int | float | str | None = None,
        limit: int | float | str | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_margin_adjustment_history(
            symbol=symbol,
            type=type,
            since=timestamp_to_int(since),
            limit=limit,
            params=params,
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_my_liquidations(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_my_liquidations(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_option(
        self,
        symbol: str,
        params: dict = {},
    ) -> dict:
        data = self.exchange.fetch_option(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    def fetch_funding_rates(
        self,
        symbols: list[str] | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_funding_rates(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    def fetch_convert_trade_history(
        self,
        code: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_convert_trade_history(
            code=code, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_bids_asks(
        self,
        symbols: list[str] | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_bids_asks(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    def fetch_orders(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_orders(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    def fetch_open_orders(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_open_orders(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    def fetch_closed_orders(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_closed_orders(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    def fetch_canceled_and_closed_orders(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.fetch_canceled_and_closed_orders(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    def fetch_order(
        self, id: str, symbol: str | None = None, params: dict = {}
    ) -> dict:
        data = self.exchange.fetch_order(id=id, symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    @staticmethod
    def order_preprocessing(func):
        @wraps(func)
        def wrapper(
            self,
            symbol: str,
            type: Literal["limit", "market"],
            side: Literal["buy", "sell"],
            amount: float | None = None,
            price: float | None = None,
            notional: float | None = None,
            *args,
            **kwargs,
        ):
            markets = (
                self.load_markets()[order_data_columns]
                .query(f"symbol == '{symbol}'")
                .to_dict("records")[0]
            )
            if type == "limit":
                if pd.isnull(price):
                    raise ValueError("Missing price for limit order.")
                else:
                    if notional is not None:
                        amount = notional / price
                    elif amount is not None:
                        notional = amount * price
                    else:
                        raise ValueError(
                            "Either notional or amount is required for limit order."
                        )
                    if notional > self.max_order_notional:
                        raise ValueError(
                            f"Order notional {notional} larger than limit {self.max_order_notional}"
                        )
                    price /= markets["precision_price"]
                    if (self.order_price_rounding == "defensive" and side == "buy") or (
                        self.order_price_rounding == "aggressive" and side == "sell"
                    ):
                        price = np.floor(price)
                    elif (
                        self.order_price_rounding == "defensive" and side == "sell"
                    ) or (self.order_price_rounding == "aggressive" and side == "buy"):
                        price = np.ceil(price)
                    else:
                        price = round(price)
                    price = np.clip(
                        price * markets["precision_price"],
                        markets["limits_price.min"],
                        markets["limits_price.max"],
                    )
            amount /= markets["precision_amount"]
            if self.order_amount_rounding == "floor":
                amount = np.floor(amount)
            elif self.order_amount_rounding == "ceil":
                amount = np.ceil(amount)
            else:
                amount = round(amount)
            amount = np.clip(
                amount * markets["precision_amount"],
                markets["limits_amount.min"],
                markets["limits_amount.max"],
            )
            return func(
                self,
                symbol=symbol,
                type=type,
                side=side,
                amount=amount,
                price=price,
                notional=notional,
                *args,
                **kwargs,
            )

        return wrapper

    @staticmethod
    def orders_dataframe_preprocessing(func):
        @wraps(func)
        def wrapper(
            self,
            orders: pd.DataFrame,
            *args,
            **kwargs,
        ):
            # Format datetime
            orders = date_time_columns_to_int_str(orders)
            if {"amount", "price"}.issubset(orders.columns):
                orders["notional"] = orders["amount"] * orders["price"]
            elif {"notional", "price"}.issubset(orders.columns):
                orders["amount"] = orders["notional"] / orders["price"]

            # Limit checks
            if "notional" in orders.columns:
                if orders.eval(f"notional > {self.max_order_notional}").any():
                    errors = orders.query(f"notional > {self.max_order_notional}")
                    raise ValueError(
                        f"Certain orders have notional larger than max notional {self.max_number_of_orders}:\n {errors}"
                    )
            n_orders = len(orders.index)
            if n_orders > self.max_number_of_orders:
                raise ValueError(
                    f"Number of orders {n_orders} larger than limit {self.max_number_of_orders}"
                )

            markets = self.load_markets()[order_data_columns]
            orders = orders.merge(markets)
            # Round values appropriately
            if "price" in orders.columns:
                orders["price"] /= orders["precision_price"]
                orders["price_down"] = np.floor(orders["price"])
                orders["price_up"] = np.floor(orders["price"])
                if self.order_price_rounding == "defensive":
                    orders["price"] = orders["price_down"].where(
                        orders["side"] == "buy", other=orders["price_up"]
                    )
                elif self.order_price_rounding == "aggressive":
                    orders["price"] = orders["price_up"].where(
                        orders["side"] == "buy", other=orders["price_down"]
                    )
                else:
                    orders["price"] = orders["price"].round()
                orders = orders.drop(columns=["price_down", "price_up"])
                orders["price"] = (orders["price"] * orders["precision_price"]).clip(
                    lower=orders["limits_price.min"], upper=orders["limits_price.max"]
                )
            orders["amount"] /= orders["precision_amount"]
            if self.order_amount_rounding == "floor":
                orders["amount"] = np.floor(orders["amount"])
            elif self.order_amount_rounding == "ceil":
                orders["amount"] = np.ceil(orders["amount"])
            else:
                orders["amount"] = orders["amount"].round()
            orders["amount"] = (orders["amount"] * orders["precision_amount"]).clip(
                lower=orders["limits_amount.min"], upper=orders["limits_amount.max"]
            )

            # Serialize param columns
            param_cols = orders.columns[orders.columns.str.startswith("params.")]
            orders["params"] = orders.apply(
                combine_params, axis=1, param_cols=param_cols
            )
            orders = ccxt_processor.orders_to_dict(orders)
            return func(
                self,
                orders=orders,
                *args,
                **kwargs,
            )

        return wrapper

    @order_preprocessing
    def create_order(
        self,
        symbol: str,
        type: Literal["limit", "market"],
        side: Literal["buy", "sell"],
        amount: float | None = None,
        price: float | None = None,
        notional: float | None = None,
        params: dict = {},
    ) -> dict:
        data = self.exchange.create_order(
            symbol=symbol,
            type=type,
            side=side,
            amount=amount,
            price=price,
            params=params,
        )
        return ccxt_processor.preprocess_dict(data)

    def cancel_order(
        self, id: str, symbol: str | None = None, params: dict = {}
    ) -> dict:
        data = self.exchange.cancel_order(id=id, symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    @order_preprocessing
    def edit_order(
        self,
        id: str,
        symbol: str,
        type: Literal["limit", "market"],
        side: Literal["buy", "sell"],
        amount: float | None = None,
        price: float | None = None,
        notional: float | None = None,
        params: dict = {},
    ) -> dict:
        data = self.exchange.edit_order(
            id=id,
            symbol=symbol,
            type=type,
            side=side,
            amount=amount,
            price=price,
            params=params,
        )
        return ccxt_processor.preprocess_dict(data)

    @orders_dataframe_preprocessing
    def create_orders(
        self,
        orders: pd.DataFrame,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.create_orders(
            orders=orders.to_dict("records"),
            params=params,
        )
        return ccxt_processor.response_to_dataframe(data)

    def cancel_orders(
        self, ids: list[str], symbol: str | None = None, params: dict = {}
    ) -> pd.DataFrame:
        data = self.exchange.cancel_orders(ids=ids, symbol=symbol, params=params)
        return ccxt_processor.response_to_dataframe(data)

    def cancel_all_orders(
        self,
        symbol: str | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.cancel_all_orders(
            symbol=symbol,
            params=params,
        )
        return ccxt_processor.response_to_dataframe(data)

    @orders_dataframe_preprocessing
    def cancel_orders_for_symbols(
        self,
        orders: pd.DataFrame,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.cancel_orders_for_symbols(
            orders=orders.to_dict("records"),
        )
        return ccxt_processor.response_to_dataframe(data)

    @orders_dataframe_preprocessing
    def edit_orders(
        self,
        orders: pd.DataFrame,
        params: dict = {},
    ) -> pd.DataFrame:
        data = self.exchange.edit_orders(
            orders=orders.to_dict("records"),
            params=params,
        )
        return ccxt_processor.response_to_dataframe(data)
