from functools import wraps
from typing import Literal, Callable

import ccxt
import numpy as np
import pandas as pd
from dataclasses import dataclass, field

from cachetools.func import ttl_cache

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

    def load_markets(self, reload: bool = True, params: dict = {}) -> pd.DataFrame:
        """
        Loads market data from the exchange and caches it.

        Args:
            reload (bool, optional): Whether to force-reload market data. Defaults to True.
            params (dict, optional): Additional parameters for the exchange's market-loading function.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A DataFrame containing the market data.
        """

        @ttl_cache(ttl=self.markets_cache_time)
        def _cached_load_markets():
            return self.exchange.load_markets(reload=reload, params=params)

        data = _cached_load_markets()
        return ccxt_processor.markets_to_dataframe(data)

    def fetch_balance(self, params: dict = {}) -> pd.DataFrame:
        """
        Fetches the account balance and converts it to a pandas DataFrame.

        Args:
            params (dict, optional): Additional parameters for the balance-fetching request.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A DataFrame containing the account balance details.
        """
        data = self.exchange.fetch_balance(params=params)
        return ccxt_processor.balance_to_dataframe(data)

    def fetch_positions_risk(
        self, symbols: list[str] | None = None, params: dict = {}
    ) -> pd.DataFrame:
        """
        Fetches risk data for open positions and converts it to a pandas DataFrame.

        Args:
            symbols (list[str] | None, optional): A list of trading symbols to filter positions.
                Defaults to None, which fetches all positions.
            params (dict, optional): API request parameters. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A DataFrame containing the risk data for open positions.
        """
        data = self.exchange.fetch_positions_risk(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    def fetch_position(self, symbol: str, params: dict = {}) -> dict:
        """
        Fetch details of a specific position.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
            params (dict, optional): Additional parameters for the API request. Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the position details.
        """
        data = self.exchange.fetch_position(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    def fetch_positions(
        self, symbols: list[str] | None = None, params: dict = {}
    ) -> pd.DataFrame:
        """
        Fetch all open positions and return as a pandas DataFrame.

        Args:
            symbols (list[str] | None, optional): List of trading pairs to filter positions. Defaults to None (fetch all positions).
            params (dict, optional): Additional parameters for the positions fetch request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A DataFrame with details of all fetched positions.
        """
        data = self.exchange.fetch_positions(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    def fetch_transfers(
        self,
        code: str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetch transfer history and convert to pandas DataFrame.

        Args:
            code (str): Currency code to filter transfers (e.g., 'BTC'). Defaults to None.
            since (int | pd.Timestamp | dict | int | None, optional): Timestamp to filter from. Can be in milliseconds or as a Timestamp.
            limit (int): Max number of records to retrieve. Defaults to None.
            params (dict): Extra parameters for the request. Defaults to {}.

        Returns:
            pd.DataFrame: DataFrame with transfer history data.
        """
        data = self.exchange.fetch_transfers(
            code=code, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_ledger(
        self,
        code: str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Retrieves the account ledger from the exchange and converts it into a pandas DataFrame.

        Args:
            code (str, optional): Currency code (e.g., 'BTC') to filter the ledger entries.
                Defaults to None, which retrieves all currencies.
            since (int | pd.Timestamp | dict | int | None, optional): A timestamp or pandas Timestamp indicating the starting date
                for fetching ledger entries. Should be in milliseconds if integer. Defaults to None, which retrieves
                all available entries.
            limit (int, optional): The maximum number of ledger records to retrieve.
                Defaults to None, fetching as many as allowed by the exchange.
            params (dict, optional): Additional parameters to pass to the exchange API for fetching the ledger.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing ledger data, formatted for easier analysis.
        """
        data = self.exchange.fetch_ledger(
            code=code, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_withdrawals(
        self,
        symbol: str = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetches the withdrawal history from the exchange and converts it into a pandas DataFrame.

        Args:
            symbol (str, optional): The trading pair symbol (e.g., 'BTC/USDT') to filter withdrawals.
                Defaults to None, which fetches data for all symbols.
            since (int | pd.Timestamp | dict | int | None, optional): A timestamp (in milliseconds) or pandas Timestamp
                to fetch data starting from that time. Defaults to None, retrieving the full history.
            limit (int, optional): Maximum number of withdrawal records to retrieve. Defaults to None.
            params (dict, optional): Additional parameters to pass to the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing withdrawal data, formatted for analysis.
        """
        data = self.exchange.fetch_withdrawals(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_currencies(self, params: dict = {}) -> pd.DataFrame:
        """
        Fetches the currencies supported by the exchange and converts them into a pandas DataFrame.

        Args:
            params (dict, optional): Additional parameters to pass to the exchange's fetch_currencies API.
                Default is an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing information about the supported currencies.
        """
        data = self.exchange.fetch_currencies(params=params)
        return ccxt_processor.markets_to_dataframe(data)

    def fetch_ticker(self, symbol: str, params: dict = {}) -> dict:
        """
        Fetches the ticker information for a specific symbol from the exchange.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
            params (dict): Additional parameters to pass to the exchange's ticker-fetching API.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the ticker data for the specified symbol, preprocessed for easier usage.
        """
        data = self.exchange.fetch_ticker(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    def fetch_tickers(
        self, symbols: list[str] | None = None, params: dict = {}
    ) -> pd.DataFrame:
        """
        Fetches ticker information for multiple symbols from the exchange.

        Args:
            symbols (list[str] | None, optional): A list of trading symbols (e.g., ['BTC/USDT', 'ETH/USDT']).
                If None, all available tickers will be fetched. Defaults to None.
            params (dict, optional): Additional parameters to be sent in the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing ticker information, such as last price, bid/ask data,
            percentage changes, and other trading data for requested symbols.
        """
        data = self.exchange.fetch_tickers(symbols=symbols, params=params)
        return ccxt_processor.markets_to_dataframe(data)

    def fetch_order_book(
        self, symbol: str, limit: int | None = None, params: dict = {}
    ) -> pd.DataFrame:
        """
        Fetch order book data for the specified symbol and convert it to a pandas DataFrame.

        Args:
            symbol (str): Trading pair symbol (e.g., 'BTC/USDT').
            limit (int | None, optional): Maximum number of order book entries to fetch. Defaults to None.
            params (dict, optional): Additional parameters to pass to the exchange's order book API. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the order book data, including bid/ask prices and volumes.
        """
        data = self.exchange.fetch_order_book(symbol=symbol, limit=limit, params=params)
        return ccxt_processor.order_book_to_dataframe(data)

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetch OHLCV (candlestick) data for a specific symbol from the exchange.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
            timeframe (str, optional): Timeframe for the candlestick data (e.g., '1m', '1h'). Defaults to '1m'.
            since (int | pd.Timestamp | dict | int | None, optional): Timestamp (in milliseconds) or pandas Timestamp to fetch data starting from. Defaults to None.
            limit (int | None, optional): The maximum number of candlestick records to retrieve. Defaults to None.
            params (dict, optional): Additional parameters to pass to the exchange's API. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing OHLCV data with columns for open, high, low, close, and volume.
        """
        data = self.exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since=timestamp_to_int(since),
            limit=limit,
            params=params,
        )
        data = ccxt_processor.ohlcv_to_dataframe(data)
        data["symbol"] = symbol
        return data

    def fetch_funding_history(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetch historical funding payment data for a specific symbol or all symbols.

        This method retrieves historical funding payment information from the exchange
        and converts it to a pandas DataFrame for easy manipulation and analysis.

        Args:
            symbol (str | None, optional): The trading pair symbol (e.g., 'BTC/USDT').
                If None, fetches data for all symbols. Defaults to None.
            since (int | pd.Timestamp | dict | int | None, optional): The starting timestamp to begin fetching data from.
                Can be an integer in milliseconds or a pandas Timestamp. Defaults to None.
            limit (int | None, optional): The maximum number of records to retrieve. If None, the exchange
                determines the limit. Defaults to None.
            params (dict, optional): Additional parameters to pass to the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the funding payment history
            with details such as the time, symbol, funding rate, payment amount, and other relevant fields.
        """
        data = self.exchange.fetch_funding_history(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_funding_rate_history(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetch historical funding rate data for a specific symbol.

        Args:
            symbol (str | None, optional): The trading pair symbol (e.g., 'BTC/USDT'). If None, data for all symbols will be retrieved. Defaults to None.
            since (int | pd.Timestamp | dict | int | None, optional): Timestamp (in milliseconds) or pandas Timestamp to fetch data starting from. Defaults to None.
            limit (int | None, optional): The maximum number of records to retrieve. Defaults to None.
            params (dict, optional): Additional parameters to pass to the exchange's API. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the funding rate history, with columns such as rate, funding time, and more.
        """
        data = self.exchange.fetch_funding_rate_history(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_open_interest(
        self,
        symbol: str,
        params: dict = {},
    ) -> dict:
        """
        Fetches the open interest for a given symbol.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
            params (dict, optional): Additional parameters for the API request. Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the open interest data for the specified symbol, preprocessed for cleaner usage.
        """
        data = self.exchange.fetch_open_interest(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    def fetch_open_interest_history(
        self,
        symbol: str,
        timeframe: str = "1h",
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetch the historical open interest data for a given trading pair symbol.

        Args:
            symbol (str): The trading pair symbol to fetch open interest data for (e.g., "BTC/USDT").
            timeframe (str): The timeframe to aggregate the data (e.g., "1m", "5m", "1h"). Defaults to "1h".
            since (int | pd.Timestamp | dict | int | None, optional): The starting timestamp in milliseconds or a pandas Timestamp.
                Fetches data from this point onward. Defaults to None.
            limit (int | None): The maximum number of records to retrieve. If None, the exchange determines
                the limit. Defaults to None.
            params (dict): Additional API parameters to customize the fetch request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing open interest history data. Columns include timestamps,
            open interest volume, and other market-specific fields.
        """
        data = self.exchange.fetch_open_interest_history(
            symbol=symbol,
            timeframe=timeframe,
            since=timestamp_to_int(since),
            limit=limit,
            params=params,
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_status(self, params: dict = {}) -> pd.DataFrame:
        """
        Fetch the status of the exchange and convert it to a pandas DataFrame.

        Args:
            params (dict): Additional parameters to send with the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the exchange status information.
        """
        data = self.exchange.fetch_status(params=params)
        return ccxt_processor.response_to_dataframe(data)

    def fetch_trades(
        self,
        symbol: str,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetch recent trades for a given symbol and convert the data into a pandas DataFrame.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
            since (int | pd.Timestamp | dict | int | None, optional): A timestamp (in milliseconds) or pandas Timestamp
                to fetch trades starting from. Defaults to None, which fetches recent trades.
            limit (int | None, optional): The maximum number of trade records to retrieve. Defaults to None.
            params (dict, optional): Additional parameters to send in the API request. Defaults to {}.

        Returns:
            pd.DataFrame: A pandas DataFrame containing recent trade data, including price, volume, and timestamp.
        """
        data = self.exchange.fetch_trades(
            symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_my_trades(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """Fetches the user's trade history and converts it to a pandas DataFrame.

        Args:
            symbol (str | None, optional): The trading pair symbol (e.g., 'BTC/USDT').
                If None, fetches trades for all symbols. Defaults to None.
            since (int | pd.Timestamp | dict | int | None, optional): A timestamp or pandas.Timestamp
                to fetch trades starting from. Should be in milliseconds if an integer. Defaults to None.
            limit (int | None, optional): Maximum number of trades to retrieve. Defaults to None.
            params (dict, optional): Additional parameters for the API request. Defaults to {}.

        Returns:
            pd.DataFrame: A DataFrame containing the user's trade history, with columns
            such as price, amount, and other relevant trade details.
        """
        data = self.exchange.fetch_my_trades(
            symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_leverages(
        self, symbols: list[str] | None = None, params: dict = {}
    ) -> pd.DataFrame:
        """
        Fetches leverage data for specified trading symbols from the exchange.

        Args:
            symbols (list[str] | None, optional): A list of trading pair symbols to filter leverages.
                If None, all symbols are fetched. Defaults to None.
            params (dict, optional): Additional parameters to include in the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing leverage data for the specified symbols.
        """
        data = self.exchange.fetch_leverages(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    def fetch_liquidations(
        self,
        symbol: str,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetches liquidation events for a specific trading pair symbol.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
            since (int | pd.Timestamp | dict | int | None, optional): Starting timestamp for fetching liquidations.
                Can be provided in milliseconds or as a pandas Timestamp. Defaults to None.
            limit (int, optional): The maximum number of liquidation events to retrieve. Defaults to None.
            params (dict, optional): Additional parameters to be sent with the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing liquidation events, including details
            such as price, volume, datetime, and other relevant information.
        """
        data = self.exchange.fetch_liquidations(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_greeks(
        self,
        symbol: str | None = None,
        params: dict = {},
    ) -> dict:
        """
        Fetch options greeks (delta, gamma, vega, theta) for a specific symbol.

        Args:
            symbol (str | None): The trading pair symbol (e.g., 'BTC/USDT').
                If None, fetches greeks for all symbols. Defaults to None.
            params (dict): Additional API parameters to include in the request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the greeks data, preprocessed for use.
        """
        data = self.exchange.fetch_greeks(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    def fetch_long_short_ratio_history(
        self,
        symbol: str | None = None,
        timeframe: str | None = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetches the historical long-short ratio for a specific symbol.

        Args:
            symbol (str | None, optional): The trading pair symbol (e.g., 'BTC/USDT').
                If None, fetches data for all available symbols. Defaults to None.
            timeframe (str | None, optional): The aggregation timeframe (e.g., '1m', '1h', '1d').
                Defaults to None, which uses the exchange's default timeframe.
            since (int | pd.Timestamp | dict | int | None, optional): A starting timestamp (in milliseconds)
                or pandas.Timestamp for fetching data from that time onward. Defaults to None.
            limit (int | None, optional): The maximum number of records to fetch.
                Defaults to None, allowing the exchange to determine the limit.
            params (dict, optional): Additional parameters to pass to the API request.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing long-short ratio history
            with columns specific to the exchange's response format.
        """
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
        """
        Fetches historical margin adjustment data for a specific symbol or all symbols.

        Args:
            symbol (str | None, optional): The trading pair symbol (e.g., 'BTC/USDT').
                If None, fetch data for all available symbols. Defaults to None.
            type (str | None, optional): The type of margin adjustment to filter (e.g., 'increase', 'decrease').
                If None, all types are included. Defaults to None.
            since (int | float | str | None, optional): Timestamp (in milliseconds) or string representation of the
                starting time to fetch data from. Defaults to None, which retrieves all available records.
            limit (int | float | str | None, optional): The maximum number of records to fetch. Defaults to None,
                fetching as many records as allowed by the exchange.
            params (dict, optional): Additional parameters to pass to the exchange API for customized requests.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing historical margin adjustment data.
        """
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
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetches the user's liquidation history and converts it to a pandas DataFrame.

        Args:
            symbol (str | None, optional): The trading pair symbol (e.g., 'BTC/USDT').
                If None, fetches liquidations for all symbols. Defaults to None.
            since (int | pd.Timestamp | dict | int | None, optional): A timestamp or pandas.Timestamp
                from which to fetch liquidations. Should be in milliseconds if an integer.
                Defaults to None.
            limit (int | None, optional): Maximum number of liquidation records to retrieve.
                Defaults to None.
            params (dict, optional): Additional parameters to include in the API request.
                Defaults to {}.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the user's liquidation history,
            including fields such as symbol, amount, price, and timestamp.
        """
        data = self.exchange.fetch_my_liquidations(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_option(
        self,
        symbol: str,
        params: dict = {},
    ) -> dict:
        """
        Fetches details of a specific option from the exchange.

        Args:
            symbol (str): The trading pair symbol or option symbol (e.g., 'BTC/USDT').
            params (dict, optional): Additional parameters to pass to the exchange's API request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing details about the specified option, preprocessed for easy usage.
        """
        data = self.exchange.fetch_option(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    def fetch_funding_rates(
        self,
        symbols: list[str] | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetches funding rates for the specified symbols from the exchange.

        Args:
            symbols (list[str] | None, optional): A list of trading pair symbols (e.g., ['BTC/USDT', 'ETH/USDT'])
                for which to fetch the funding rates. Defaults to None, which fetches funding rates for all available symbols.
            params (dict, optional): Additional parameters to pass to the API request.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing funding rate data for the specified symbols,
            including fields such as symbol, rate, and timestamp.

        """
        data = self.exchange.fetch_funding_rates(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    def fetch_convert_trade_history(
        self,
        code: str | None = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetches historical convert trade data from the exchange.

        Args:
            code (str | None, optional): The currency code for which to fetch the
                trade history (e.g., 'BTC'). Defaults to None.
            since (int | pd.Timestamp | dict | int | None, optional): The starting timestamp to
                fetch data from. Can be an integer in milliseconds or a pandas
                Timestamp. Defaults to None.
            limit (int | None, optional): The maximum number of records to fetch.
                Defaults to None, fetching the exchange-defined default limit.
            params (dict, optional): Additional parameters to pass to the API request.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the historical convert
            trade data, including fields such as the currency, amount, and timestamp.
        """
        data = self.exchange.fetch_convert_trade_history(
            code=code, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    def fetch_bids_asks(
        self,
        symbols: list[str] | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetch the latest bid and ask prices for multiple symbols.

        Args:
            symbols (list[str] | None, optional): A list of trading pair symbols (e.g., ['BTC/USDT', 'ETH/USDT']).
                If None, fetches bid/ask prices for all available symbols. Defaults to None.
            params (dict, optional): Additional parameters for the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the latest bid and ask prices
            for the requested symbols, including relevant market data.
        """
        data = self.exchange.fetch_bids_asks(symbols=symbols, params=params)
        return ccxt_processor.markets_to_dataframe(data)

    def fetch_orders(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetches order history from the exchange and converts it to a pandas DataFrame.

        Args:
            symbol (str | None): Trading pair symbol (e.g., 'BTC/USDT'). Defaults to None, which fetches orders for all symbols.
            since (int | pd.Timestamp | dict | int | None, optional): A timestamp (milliseconds or pandas Timestamp) to fetch orders starting from. Defaults to None.
            limit (int | None): Maximum number of orders to retrieve. Defaults to None.
            params (dict): Additional parameters for the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A DataFrame containing the order history, with fields such as order ID, status, price, and volume.
        """
        data = self.exchange.fetch_orders(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    def fetch_open_orders(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetches open orders from the exchange and converts them to a pandas DataFrame.

        Args:
            symbol (str | None): Trading pair symbol to filter open orders (e.g., 'BTC/USDT'). Defaults to None, which fetches all open orders.
            since (int | pd.Timestamp | dict | int | None, optional): A timestamp (milliseconds or pandas Timestamp) to fetch open orders starting from. Defaults to None.
            limit (int | None): Maximum number of open orders to retrieve. Defaults to None.
            params (dict): Additional parameters for the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A DataFrame containing open orders, including fields for status, amount, price, and timestamp.
        """
        data = self.exchange.fetch_open_orders(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    def fetch_closed_orders(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetch closed orders from the exchange and convert them to a pandas DataFrame.

        Args:
            symbol (str | None): Trading pair symbol to filter closed orders (e.g., "BTC/USDT").
                Defaults to None, which fetches all closed orders.
            since (int | pd.Timestamp | dict | int | None, optional): Timestamp (in milliseconds or pandas.Timestamp) indicating
                the starting point for fetching closed orders. Defaults to None.
            limit (int | None): Maximum number of closed orders to retrieve.
                Defaults to None, using the exchange's default limit.
            params (dict): Additional parameters for the API request.

        Returns:
            pd.DataFrame: A DataFrame containing information about closed orders, including details
                such as status, price, volume, and execution time.
        """
        data = self.exchange.fetch_closed_orders(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    def fetch_canceled_and_closed_orders(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | dict | str | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetches canceled and closed orders from the exchange and converts them to a pandas DataFrame.

        Args:
            symbol: Trading pair symbol to filter canceled and closed orders (e.g., 'BTC/USDT').
                Defaults to None, retrieving all such orders.
            since: Timestamp (milliseconds or pandas Timestamp) to fetch orders starting from.
                Defaults to None.
            limit: Maximum number of orders (canceled and closed) to retrieve.
                Defaults to None.
            params: Additional parameters for the API request.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A DataFrame containing canceled and closed orders, with fields
            such as order type, price, and time.
        """
        data = self.exchange.fetch_canceled_and_closed_orders(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    def fetch_order(
        self, id: str, symbol: str | None = None, params: dict = {}
    ) -> dict:
        """
        Fetch a specific order by its ID and optionally filter by symbol.

        Args:
            id (str): The unique order ID to retrieve.
            symbol (str | None, optional): The trading pair symbol (e.g., 'BTC/USDT')
                associated with the order. Defaults to None.
            params (dict, optional): Additional parameters to pass in the API request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing details about the requested order after preprocessing.
        """
        data = self.exchange.fetch_order(id=id, symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    @staticmethod
    def order_preprocessing(func: Callable):
        """
        A decorator for preprocessing order parameters such as price, amount, and notional
        before creating, editing, or manipulating orders.

        Args:
            func (Callable): The function to be wrapped and modified with preprocessing logic.

        Returns:
            Callable: The decorated function with added preprocessing for order parameters.
        """

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

    def orders_dataframe_preprocessing(self, orders: pd.DataFrame) -> list:
        """
        Preprocesses a DataFrame containing orders to validate, format, and adjust values.

        This method ensures proper formatting of datetime fields, calculates notional values
        if not present, checks for notional and order count limits, and rounds price and
        amount fields based on the rounding rules and precision constraints of the exchange.

        Args:
            orders (pd.DataFrame): A DataFrame where each row represents an order with fields
                such as 'symbol', 'amount', 'price', 'side', and optional params.

        Returns:
            list: A list of preprocessed order dictionaries, ready for API submission.

        Raises:
            ValueError: If any order exceeds the max notional value, if the number of orders
                exceeds the max allowed, or if required fields are missing during the preprocessing.
        """
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
        orders["params"] = orders.apply(combine_params, axis=1, param_cols=param_cols)
        return ccxt_processor.orders_to_dict(orders)

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
        """
        Create a new order after preprocessing.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
            type (Literal["limit", "market"]): Order type, either 'limit' or 'market'.
            side (Literal["buy", "sell"]): Order side, either 'buy' or 'sell'.
            amount (float | None, optional): The quantity of the asset to trade. Defaults to None.
            price (float | None, optional): The target price for the order. Required for limit orders. Defaults to None.
            notional (float | None, optional): The total trade value. Either `amount` or `notional` must be specified. Defaults to None.
            params (dict, optional): Additional parameters to include when creating the order. Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the order details, preprocessed and formatted.

        Raises:
            ValueError: If required arguments (e.g., price for limit orders or amount/notional) are missing or invalid.
        """
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
        """
        Cancels an existing order by its ID.

        Args:
            id (str): The unique order ID to cancel.
            symbol (str | None): The trading pair symbol (e.g., 'BTC/USDT') associated with the order.
                Defaults to None, which allows the exchange to determine the symbol.
            params (dict): Additional parameters for customization during the API request.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary with the details of the canceled order after preprocessing.
        """
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
        """
        Edit an existing order with specific parameters.

        This function allows modification of an existing order on the exchange. It preprocesses the input
        parameters to meet the exchange requirements and then updates the order.

        Args:
            id (str): The ID of the order to be edited.
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
            type (Literal["limit", "market"]): Type of order. Either 'limit' or 'market'.
            side (Literal["buy", "sell"]): The action for the order. Either 'buy' or 'sell'.
            amount (float | None, optional): The quantity of the asset to trade. Defaults to None.
            price (float | None, optional): The target price for the order. Required for limit orders. Defaults to None.
            notional (float | None, optional): The total value of the trade. Either `amount` or `notional` must be provided. Defaults to None.
            params (dict, optional): Additional parameters for the order request. Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the updated details of the modified order, preprocessed for easy use.

        Raises:
            ValueError: If required arguments (e.g., price for limit orders or amount/notional) are missing or invalid.
        """
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

    def create_orders(
        self,
        orders: pd.DataFrame,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Create multiple orders in a batch.

        This method creates multiple orders using data provided in a pandas
        DataFrame. It preprocesses the orders to ensure they meet exchange
        requirements before submission.

        Args:
            orders (pd.DataFrame): A DataFrame containing order information.
                Each row represents an order with columns such as `symbol`,
                `amount`, `price`, and `side`.
            params (dict, optional): Additional parameters to include for each
                order during API requests. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the response from the
            exchange, including details about created orders.
        """
        data = self.exchange.create_orders(
            orders=self.orders_dataframe_preprocessing(orders=orders),
            params=params,
        )
        return ccxt_processor.response_to_dataframe(data)

    def cancel_orders(
        self, ids: list[str], symbol: str | None = None, params: dict = {}
    ) -> pd.DataFrame:
        """
        Cancel multiple orders using their IDs and return the cancellation details as a pandas DataFrame.

        Args:
            ids (list[str]): A list of order IDs to cancel.
            symbol (str | None, optional): The trading pair symbol (e.g., 'BTC/USDT') associated with the orders.
                If None, cancels orders across all symbols. Defaults to None.
            params (dict, optional): Additional parameters to customize the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing details about the canceled orders.

        """
        data = self.exchange.cancel_orders(ids=ids, symbol=symbol, params=params)
        return ccxt_processor.response_to_dataframe(data)

    def cancel_all_orders(
        self,
        symbol: str | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Cancel all orders for a given symbol or across all symbols.

        Args:
            symbol (str | None, optional): The trading pair symbol (e.g., 'BTC/USDT'). If None, all orders across symbols
                will be canceled. Defaults to None.
            params (dict, optional): Additional parameters to include in the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing details about the canceled orders.
        """
        data = self.exchange.cancel_all_orders(
            symbol=symbol,
            params=params,
        )
        return ccxt_processor.response_to_dataframe(data)

    def cancel_orders_for_symbols(
        self,
        orders: pd.DataFrame,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Cancel multiple orders across different symbols in a batch.

        This method cancels multiple orders supplied in a pandas DataFrame. It preprocesses
        the orders to ensure they meet exchange requirements before attempting to cancel them.

        Args:
            orders (pd.DataFrame):
                A pandas DataFrame where each row represents an order, including
                fields such as `symbol` (trading pair) and `id` (order id).
            params (dict, optional):
                Extra parameters to include during the cancel request for enhanced
                API customization. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame:
                A pandas DataFrame containing information regarding the canceled
                orders, including order ID, status, symbol, and other details.
        """
        data = self.exchange.cancel_orders_for_symbols(
            orders=orders[["id", "symbol"]].to_dict("records"),
        )
        return ccxt_processor.response_to_dataframe(data)

    def edit_orders(
        self,
        orders: pd.DataFrame,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Edit multiple orders in a batch.

        This method allows batch editing of multiple orders provided in a pandas DataFrame.
        It ensures that the orders meet the exchange requirements by preprocessing the `orders` DataFrame.

        Args:
            orders (pd.DataFrame): A pandas DataFrame containing the updated order information.
                Each row represents an order and must include appropriate fields (e.g., `id`, `symbol`, etc.).
            params (dict, optional): Additional global parameters to include in the API request during batch updates.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the responses from the exchange for each edited order.
                Each row corresponds to an order update response.

        Raises:
            ValueError: If preprocessing of the `orders` DataFrame fails due to missing or invalid data fields.
        """
        data = self.exchange.edit_orders(
            orders=self.orders_dataframe_preprocessing(orders=orders),
            params=params,
        )
        return ccxt_processor.response_to_dataframe(data)
