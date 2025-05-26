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
        self, reload: bool = True, params: dict = {}
    ) -> pd.DataFrame:
        """
        Loads market data from the exchange and caches it.

        Args:
            reload (bool, optional): Whether to force-reload market data. Defaults to True.
            params (dict, optional): Additional parameters for the exchange's market-loading function.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A DataFrame containing the market data.
        """
        data = await self.exchange.load_markets(reload=reload, params=params)
        return ccxt_processor.markets_to_dataframe(data)

    async def fetch_balance(self, params: dict = {}) -> pd.DataFrame:
        """Fetches the account balance and converts it to a pandas DataFrame.

        Args:
            params (dict, optional): Additional parameters for the balance-fetching request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A DataFrame containing the account balance details.
        """
        data = await self.exchange.fetch_balance(params=params)
        return ccxt_processor.balance_to_dataframe(data)

    async def fetch_positions_risk(
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
        data = await self.exchange.fetch_positions_risk(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_position(self, symbol: str, params: dict = {}) -> dict:
        """
        Fetch details of a specific position.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
            params (dict, optional): Additional parameters for the API request. Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the position details.
        """
        data = await self.exchange.fetch_position(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    async def fetch_positions(
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
        data = await self.exchange.fetch_positions(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_transfers(
        self,
        code: str = None,
        since: int | pd.Timestamp | None = None,
        limit: int = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetch transfer history and convert to pandas DataFrame.

        Args:
            code (str): Currency code to filter transfers (e.g., 'BTC'). Defaults to None.
            since (int | pd.Timestamp | None): Timestamp to filter from. Can be in milliseconds or as a Timestamp.
            limit (int): Max number of records to retrieve. Defaults to None.
            params (dict): Extra parameters for the request. Defaults to {}.

        Returns:
            pd.DataFrame: DataFrame with transfer history data.
        """
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
        """
        Retrieves the account ledger from the exchange and converts it into a pandas DataFrame.

        Args:
            code (str, optional): Currency code (e.g., 'BTC') to filter the ledger entries.
                Defaults to None, which retrieves all currencies.
            since (int | pd.Timestamp | None, optional): A timestamp or pandas Timestamp indicating the starting date
                for fetching ledger entries. Should be in milliseconds if integer. Defaults to None, which retrieves
                all available entries.
            limit (int, optional): The maximum number of ledger records to retrieve.
                Defaults to None, fetching as many as allowed by the exchange.
            params (dict, optional): Additional parameters to pass to the exchange API for fetching the ledger.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing ledger data, formatted for easier analysis.
        """
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
        """
        Fetches the withdrawal history from the exchange and converts it into a pandas DataFrame.

        Args:
            symbol (str, optional): The trading pair symbol (e.g., 'BTC/USDT') to filter withdrawals.
                Defaults to None, which fetches data for all symbols.
            since (int | pd.Timestamp | None, optional): A timestamp (in milliseconds) or pandas Timestamp
                to fetch data starting from that time. Defaults to None, retrieving the full history.
            limit (int, optional): Maximum number of withdrawal records to retrieve. Defaults to None.
            params (dict, optional): Additional parameters to pass to the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing withdrawal data, formatted for analysis.
        """
        data = await self.exchange.fetch_withdrawals(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_currencies(self, params: dict = {}) -> pd.DataFrame:
        """
        Fetches the currencies supported by the exchange and converts them into a pandas DataFrame.

        Args:
            params (dict, optional): Additional parameters to pass to the exchange's fetch_currencies API.
                Default is an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing information about the supported currencies.
        """
        data = await self.exchange.fetch_currencies(params=params)
        return ccxt_processor.markets_to_dataframe(data)

    async def fetch_ticker(self, symbol: str, params: dict = {}) -> dict:
        """
        Fetches the ticker information for a specific symbol from the exchange.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
            params (dict): Additional parameters to pass to the exchange's ticker-fetching API.
                Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the ticker data for the specified symbol, preprocessed for easier usage.
        """
        data = await self.exchange.fetch_ticker(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    async def fetch_tickers(
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
        data = await self.exchange.fetch_tickers(symbols=symbols, params=params)
        return ccxt_processor.markets_to_dataframe(data)

    async def fetch_order_book(
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
        """Fetch OHLCV (candlestick) data for a specific symbol from the exchange.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
            timeframe (str, optional): Timeframe for the candlestick data (e.g., '1m', '1h'). Defaults to '1m'.
            since (int | pd.Timestamp | None, optional): A timestamp (in milliseconds) or pandas.Timestamp to fetch data starting from. Defaults to None.
            limit (int | None, optional): The maximum number of candlestick records to retrieve. Defaults to None.
            params (dict, optional): Additional parameters to pass to the exchange's API. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing OHLCV data with columns for open, high, low, close, and volume.
        """
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
        """Fetch historical funding rate data for a specific symbol.

        Args:
            symbol (str | None, optional): The trading pair symbol (e.g., 'BTC/USDT'). If None, data for all symbols will be retrieved. Defaults to None.
            since (int | pd.Timestamp | None, optional): A timestamp (in milliseconds) or pandas.Timestamp to fetch data starting from. Defaults to None.
            limit (int | None, optional): The maximum number of records to retrieve. Defaults to None.
            params (dict, optional): Additional parameters to pass to the exchange's API. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the funding rate history, with columns such as rate, funding time, and more.
        """
        data = await self.exchange.fetch_funding_rate_history(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_open_interest(
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
        """
        Fetch the historical open interest data for a given trading pair symbol.

        Args:
            symbol (str): The trading pair symbol to fetch open interest data for (e.g., "BTC/USDT").
            timeframe (str): The timeframe to aggregate the data (e.g., "1m", "5m", "1h"). Defaults to "1h".
            since (int | pd.Timestamp | None): The starting timestamp in milliseconds or a pandas Timestamp.
                Fetches data from this point onward. Defaults to None.
            limit (int | None): The maximum number of records to retrieve. If None, the exchange determines
                the limit. Defaults to None.
            params (dict): Additional API parameters to customize the fetch request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing open interest history data. Columns include timestamps,
            open interest volume, and other market-specific fields.
        """
        data = await self.exchange.fetch_open_interest_history(
            symbol=symbol,
            timeframe=timeframe,
            since=timestamp_to_int(since),
            limit=limit,
            params=params,
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_status(self, params: dict = {}) -> pd.DataFrame:
        """
        Fetch the status of the exchange and convert it to a pandas DataFrame.

        Args:
            params (dict): Additional parameters to send with the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the exchange status information.
        """
        data = await self.exchange.fetch_status(params=params)
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_trades(
        self,
        symbol: str,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetch recent trades for a given symbol and convert the data into a pandas DataFrame.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
            since (int | pd.Timestamp | None, optional): A timestamp (in milliseconds) or pandas Timestamp
                to fetch trades starting from. Defaults to None, which fetches recent trades.
            limit (int | None, optional): The maximum number of trade records to retrieve. Defaults to None.
            params (dict, optional): Additional parameters to send in the API request. Defaults to {}.

        Returns:
            pd.DataFrame: A pandas DataFrame containing recent trade data, including price, volume, and timestamp.
        """
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
        """Fetches the user's trade history and converts it to a pandas DataFrame.

        Args:
            symbol (str | None, optional): The trading pair symbol (e.g., 'BTC/USDT').
                If None, fetches trades for all symbols. Defaults to None.
            since (int | pd.Timestamp | None, optional): A timestamp or pandas.Timestamp
                to fetch trades starting from. Should be in milliseconds if an integer. Defaults to None.
            limit (int | None, optional): Maximum number of trades to retrieve. Defaults to None.
            params (dict, optional): Additional parameters for the API request. Defaults to {}.

        Returns:
            pd.DataFrame: A DataFrame containing the user's trade history, with columns
            such as price, amount, and other relevant trade details.
        """
        data = await self.exchange.fetch_my_trades(
            symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_leverages(
        self, symbols: list[str] | None = None, params: dict = {}
    ) -> pd.DataFrame:
        """Fetches leverage data for specified trading symbols from the exchange.

        Args:
            symbols (list[str] | None, optional): A list of trading pair symbols to filter leverages. If None, all symbols are fetched. Defaults to None.
            params (dict, optional): Additional parameters to include in the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing leverage data for the specified symbols.
        """
        data = await self.exchange.fetch_leverages(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_liquidations(
        self,
        symbol: str,
        since: int | pd.Timestamp | None = None,
        limit: int = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetches liquidation events for a specific trading pair symbol.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT').
            since (int | pd.Timestamp | None, optional): Starting timestamp for fetching liquidations.
                Can be provided in milliseconds or as a pandas Timestamp. Defaults to None.
            limit (int, optional): The maximum number of liquidation events to retrieve. Defaults to None.
            params (dict, optional): Additional parameters to be sent with the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing liquidation events, including details
            such as price, volume, datetime, and other relevant information.
        """
        data = await self.exchange.fetch_liquidations(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_greeks(
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
        """
        Fetches the historical long-short ratio for a specific symbol.

        Args:
            symbol (str | None, optional): The trading pair symbol (e.g., 'BTC/USDT').
                If None, fetches data for all available symbols. Defaults to None.
            timeframe (str | None, optional): The aggregation timeframe (e.g., '1m', '1h', '1d').
                Defaults to None, which uses the exchange's default timeframe.
            since (int | pd.Timestamp | None, optional): A starting timestamp (in milliseconds)
                or pandas.Timestamp for fetching data from that time onward. Defaults to None.
            limit (int | None, optional): The maximum number of records to fetch.
                Defaults to None, allowing the exchange to determine the limit.
            params (dict, optional): Additional parameters to pass to the API request.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing long-short ratio history
            with columns specific to the exchange's response format.
        """
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
        """
        Fetches the user's liquidation history and converts it to a pandas DataFrame.

        Args:
            symbol (str | None, optional): The trading pair symbol (e.g., 'BTC/USDT').
                If None, fetches liquidations for all symbols. Defaults to None.
            since (int | pd.Timestamp | None, optional): A timestamp or pandas.Timestamp
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
        data = await self.exchange.fetch_my_liquidations(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_option(
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
        data = await self.exchange.fetch_option(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    async def fetch_funding_rates(
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
        data = await self.exchange.fetch_funding_rates(symbols=symbols, params=params)
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_convert_trade_history(
        self,
        code: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetches historical convert trade data from the exchange.

        Args:
            code (str | None, optional): The currency code for which to fetch the
                trade history (e.g., 'BTC'). Defaults to None.
            since (int | pd.Timestamp | None, optional): The starting timestamp to
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
        data = await self.exchange.fetch_convert_trade_history(
            code=code, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def fetch_bids_asks(
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
        data = await self.exchange.fetch_bids_asks(symbols=symbols, params=params)
        return ccxt_processor.markets_to_dataframe(data)

    async def fetch_orders(
        self,
        symbol: str | None = None,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Fetches order history from the exchange and converts it to a pandas DataFrame.

        Args:
            symbol (str | None): Trading pair symbol (e.g., 'BTC/USDT'). Defaults to None, which fetches orders for all symbols.
            since (int | pd.Timestamp | None): A timestamp (milliseconds or pandas Timestamp) to fetch orders starting from. Defaults to None.
            limit (int | None): Maximum number of orders to retrieve. Defaults to None.
            params (dict): Additional parameters for the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A DataFrame containing the order history, with fields such as order ID, status, price, and volume.
        """
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
        """Fetches open orders from the exchange and converts them to a pandas DataFrame.

        Args:
            symbol (str | None, optional): Trading pair symbol to filter open orders (e.g., 'BTC/USDT'). Defaults to None, which fetches all open orders.
            since (int | pd.Timestamp | None, optional): A timestamp (in milliseconds or pandas.Timestamp) to fetch open orders starting from. Defaults to None.
            limit (int | None, optional): Maximum number of open orders to retrieve. Defaults to None.
            params (dict, optional): Additional parameters for the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A DataFrame containing open orders, including fields for status, amount, price, and timestamp.
        """
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
        """
        Fetch closed orders from the exchange and convert them to a pandas DataFrame.

        Args:
            symbol (str | None): Trading pair symbol to filter closed orders (e.g., "BTC/USDT").
                Defaults to None, which fetches all closed orders.
            since (int | pd.Timestamp | None): Timestamp (in milliseconds or pandas.Timestamp) indicating
                the starting point for fetching closed orders. Defaults to None.
            limit (int | None): Maximum number of closed orders to retrieve.
                Defaults to None, using the exchange's default limit.
            params (dict): Additional parameters for the API request.

        Returns:
            pd.DataFrame: A DataFrame containing information about closed orders, including details
                such as status, price, volume, and execution time.
        """
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
        data = await self.exchange.fetch_canceled_and_closed_orders(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.orders_to_dataframe(data)

    async def fetch_order(
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
        data = await self.exchange.fetch_order(id=id, symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    async def watch_liquidations(
        self,
        symbol: str,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Watch real-time liquidation events for a specific trading pair symbol.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT') to monitor.
            since (int | pd.Timestamp | None, optional): A timestamp (in milliseconds) or pandas.Timestamp
                specifying the starting point for watching liquidations. Defaults to None.
            limit (int | None, optional): The maximum number of liquidation events to fetch.
                Default is determined by the exchange.
            params (dict, optional): Additional parameters to include in the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A DataFrame containing real-time liquidation data, such as price, volume, and timestamps,
            formatted for analysis.
        """
        data = await self.exchange.watch_liquidations(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def watch_liquidations_for_symbols(
        self,
        symbols: list[str],
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Watch real-time liquidation events for multiple trading pair symbols.

        Args:
            symbols (list[str]): A list of trading pair symbols (e.g., ['BTC/USDT', 'ETH/USDT'])
                to monitor for liquidation events.
            since (int | pd.Timestamp | None, optional): A timestamp (in milliseconds) or pandas.Timestamp
                specifying the starting point for watching liquidations. Defaults to None.
            limit (int | None, optional): The maximum number of liquidation events to fetch
                per symbol. Default is determined by the exchange.
            params (dict, optional): Additional parameters to include in the API request.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing real-time liquidation data for the requested
            symbols, such as price, volume, event time, and other metadata, formatted for analysis.
        """
        data = await self.exchange.watch_liquidations_for_symbols(
            symbols=symbols, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def watch_ticker(self, symbol: str, params: dict = {}) -> dict:
        """
        Watch real-time ticker updates for the specified trading symbol.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT') to monitor for real-time ticker updates.
            params (dict, optional): Additional parameters for the API request. Defaults to an empty dictionary.

        Returns:
            dict: A dictionary containing the real-time ticker data, including information such as last price,
                bid/ask data, percentage changes, and other market-specific fields, preprocessed for analysis.
        """
        data = await self.exchange.watch_ticker(symbol=symbol, params=params)
        return ccxt_processor.preprocess_dict(data)

    async def watch_orders(
        self,
        symbol: str,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Watch real-time order updates for the specified trading pair symbol.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT') to monitor for real-time order updates.
            since (int | pd.Timestamp | None, optional): A starting timestamp (in milliseconds or pandas.Timestamp)
                to watch orders from. Defaults to None.
            limit (int | None, optional): The maximum number of orders to watch. Defaults to None, determined by the exchange.
            params (dict, optional): Additional API request parameters. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing real-time order updates, including order ID, status, price,
            amount, and other relevant fields.
        """
        data = await self.exchange.watch_orders(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def watch_orders_for_symbols(
        self,
        symbols: list[str],
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Watch real-time order updates for multiple trading pair symbols.

        Args:
            symbols (list[str]): A list of trading pair symbols (e.g., ['BTC/USDT', 'ETH/USDT']) to monitor.
            since (int | pd.Timestamp | None, optional): A starting timestamp (milliseconds or pandas.Timestamp)
                to fetch updates from. Defaults to None, watching real-time from the current time.
            limit (int | None, optional): The maximum number of order updates to fetch per symbol. Defaults to None.
            params (dict, optional): Additional parameters to send with the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing real-time order updates for the provided symbols,
            with fields such as order ID, price, amount, and status.
        """
        data = await self.exchange.watch_orders_for_symbols(
            symbols=symbols, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def watch_position(
        self,
        symbol: str,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Watches real-time updates for a specific position.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT') to monitor.
            params (dict, optional): Additional parameters for the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing real-time position data, such as size, price, and timestamp.
        """
        data = await self.exchange.watch_position(symbol=symbol, params=params)
        return ccxt_processor.response_to_dataframe(data)

    async def watch_positions(
        self,
        symbols: list[str],
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Watch real-time updates for multiple positions.

        Args:
            symbols (list[str]): A list of trading pair symbols (e.g., ['BTC/USDT', 'ETH/USDT'])
                to monitor for position updates. Each symbol must be a valid trading pair on the exchange.
            since (int | pd.Timestamp | None, optional): A timestamp (in milliseconds or pandas.Timestamp)
                specifying the starting point for watching positions. Defaults to None.
            limit (int | None, optional): The maximum number of position updates to fetch. If None, the exchange's
                default limit is used. Defaults to None.
            params (dict, optional): Additional parameters to be sent with the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing real-time position updates for the requested symbols.
            Each row includes fields such as symbol, position size, entry price, unrealized PnL, and timestamps.
        """
        data = await self.exchange.watch_positions(
            symbols=symbols, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def watch_bids_asks(
        self, symbols: list[str], params: dict = {}
    ) -> pd.DataFrame:
        """
        Watch real-time bid and ask prices for specified trading symbols.

        Args:
            symbols (list[str]): A list of trading pair symbols (e.g., ['BTC/USDT', 'ETH/USDT']) to monitor.
                Each symbol must be a valid trading pair supported by the exchange.
            params (dict, optional): Additional parameters for the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing real-time bid and ask price data for the requested symbols.
            Each row includes fields such as symbol, bid price, ask price, and timestamps.
        """
        data = await self.exchange.watch_bids_asks(symbols=symbols, params=params)
        return ccxt_processor.markets_to_dataframe(data)

    async def watch_order_book(
        self, symbol: str, limit: int | None = None, params: dict = {}
    ) -> pd.DataFrame:
        """
        Watches the real-time order book for a specified trading pair symbol.

        This function fetches updates in real-time for the order book of a specific
        trading pair. It processes the data and outputs it as a pandas DataFrame,
        formatted for analysis.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT') to monitor.
            limit (int | None): The maximum number of entries to include in the
                order book. Defaults to None, where the exchange determines the limit.
            params (dict): Additional parameters to send with the API request.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the real-time order book data
            for the specified symbol. Includes bid and ask prices, volumes, and other
            relevant market data.
        """
        data = await self.exchange.watch_order_book(
            symbol=symbol, limit=limit, params=params
        )
        return ccxt_processor.order_book_to_dataframe(data)

    async def watch_order_book_for_symbols(
        self, symbols: list[str], limit: int | None = None, params: dict = {}
    ) -> pd.DataFrame:
        """
        Watches real-time updates for order books of specific trading symbols.

        Args:
            symbols (list[str]): A list of trading pair symbols (e.g., ['BTC/USDT', 'ETH/USDT'])
                to monitor for real-time order book updates.
            limit (int | None, optional): The maximum number of order book entries to fetch
                per symbol. Defaults to None, where the exchange determines the limit.
            params (dict, optional): Additional parameters to customize the API request.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing real-time order book data for the specified symbols.
            Includes bid/ask prices, volumes, and other relevant market data.
        """
        data = await self.exchange.watch_order_book_for_symbols(
            symbols=symbols, limit=limit, params=params
        )
        return ccxt_processor.order_book_to_dataframe(data)

    async def watch_my_trades(
        self,
        symbol: str,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Streams real-time user trade updates for a specific symbol.

        This function watches for the user's trade updates on a specific trading
        pair in real-time, converts the updates to a Pandas DataFrame, and formats
        the data for easy analysis.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT') to monitor.
            since (int | pd.Timestamp | None, optional): A starting timestamp (milliseconds or pandas.Timestamp)
                from which to watch trade updates. Defaults to None for current time.
            limit (int | None, optional): The maximum number of trade updates to fetch.
                If None, this will be determined by the exchange. Defaults to None.
            params (dict, optional): Additional custom parameters to include in the API request.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing real-time user trade updates, including fields
            such as trade ID, symbol, amount, price, and timestamp.
        """
        data = await self.exchange.watch_my_trades(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def watch_my_trades_for_symbols(
        self,
        symbols: list[str],
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Stream real-time user trade updates for multiple symbols.

        This method watches user trade updates on multiple trading pairs
        in real-time. It retrieves the updates for the specified trading
        symbols and converts them into a Pandas DataFrame for easy processing.

        Args:
            symbols (list[str]): A list of trading pair symbols (e.g., ['BTC/USDT', 'ETH/USDT']).
                Each symbol should be supported by the exchange.
            since (int | pd.Timestamp | None, optional): A timestamp (in milliseconds or pandas.Timestamp)
                specifying the starting point for watching trade updates. Defaults to None.
            limit (int | None, optional): The maximum number of trade updates to watch for each symbol.
                The exchange's default limit applies when None. Defaults to None.
            params (dict, optional): Custom parameters to include in the API request. Defaults to an
                empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing real-time user trade updates,
                including fields such as trade ID, symbol, amount, price, and timestamp.
        """
        data = await self.exchange.watch_my_trades_for_symbols(
            symbols=symbols, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def watch_trades(
        self,
        symbol: str,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Streams real-time trade updates for a specific trading pair symbol.

        This function watches real-time trade updates for a specified
        trading pair and converts the received data into a pandas DataFrame.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT') to monitor.
            since (int | pd.Timestamp | None, optional): The starting timestamp
                (in milliseconds or pandas.Timestamp) to watch trades from. Defaults to None.
            limit (int | None, optional): The maximum number of trade updates to fetch.
                If None, this is determined by the exchange. Defaults to None.
            params (dict, optional): Additional parameters to pass to the API request.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing real-time trade updates,
            formatted with relevant fields such as trade ID, price, amount, and timestamp.
        """
        data = await self.exchange.watch_trades(
            symbol=symbol, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def watch_trades_for_symbols(
        self,
        symbols: list[str],
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Streams real-time trade updates for multiple trading pair symbols.

        Args:
            symbols (list[str]): A list of trading pair symbols (e.g., ['BTC/USDT', 'ETH/USDT']).
                Each symbol must be a valid trading pair on the exchange.
            since (int | pd.Timestamp | None, optional): A starting timestamp in milliseconds or a pandas
                `pd.Timestamp` to specify the starting point to fetch updates. Defaults to None for
                starting from the present time.
            limit (int | None, optional): Maximum number of trade updates to fetch per symbol. Defaults to None,
                in which case the exchange determines the limit.
            params (dict, optional): Additional key-value pairs to pass in the API request. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing real-time trade data for multiple symbols. Fields in
            the DataFrame include trading pair, trade ID, price, amount, and timestamp.
        """
        data = await self.exchange.watch_trades_for_symbols(
            symbols=symbols, since=timestamp_to_int(since), limit=limit, params=params
        )
        return ccxt_processor.response_to_dataframe(data)

    async def watch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1m",
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Streams real-time OHLCV (candlestick) data for a specific trading pair symbol.

        This method watches for real-time candlestick updates and converts the
        received data into a pandas DataFrame for analysis.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTC/USDT') to monitor.
            timeframe (str, optional): The candlestick interval (e.g., '1m', '5m', '1h').
                Defaults to '1m'.
            since (int | pd.Timestamp | None, optional): A timestamp (milliseconds or pandas.Timestamp)
                specifying the starting point for fetching real-time OHLCV updates. Defaults to None.
            limit (int | None, optional): The maximum number of candlestick updates to fetch.
                Defaults to None, determined by the exchange.
            params (dict, optional): Additional API request parameters. Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing real-time OHLCV data with columns such
            as open, high, low, close, and volume. Each record represents a candlestick
            for the specified timeframe.
        """
        data = await self.exchange.watch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            since=timestamp_to_int(since),
            limit=limit,
            params=params,
        )
        return ccxt_processor.ohlcv_to_dataframe(data)

    async def watch_ohlcv_for_symbols(
        self,
        symbols_and_timeframes: pd.DataFrame,
        since: int | pd.Timestamp | None = None,
        limit: int | None = None,
        params: dict = {},
    ) -> pd.DataFrame:
        """
        Streams real-time OHLCV (candlestick) data for multiple trading pairs.

        This method streams real-time Open, High, Low, Close, Volume (OHLCV) data
        for multiple trading pairs and timeframes. It processes the responses into
        a pandas DataFrame for ease of use and analysis.

        Args:
            symbols_and_timeframes (pd.DataFrame): A DataFrame containing the list
                of symbols and their corresponding timeframes to fetch real-time
                OHLCV data. The DataFrame must include columns named "symbol"
                and "timeframe".
            since (int | pd.Timestamp | None, optional): A timestamp (milliseconds or
                pandas.Timestamp) determining where to start fetching updates.
                Defaults to None, which streams updates from the present.
            limit (int | None, optional): The maximum number of OHLCV records
                to fetch per symbol and timeframe. Defaults to None.
            params (dict, optional): Additional parameters to pass with the API request.
                Defaults to an empty dictionary.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the streamed OHLCV data.
            Each row contains details for a specific symbol and timeframe, including
            open, high, low, close, and volume.
        """
        data = await self.exchange.watch_ohlcv_for_symbols(
            symbolsAndTimeframes=symbols_and_timeframes[
                ["symbol", "timeframe"]
            ].values.tolist(),
            since=timestamp_to_int(since),
            limit=limit,
            params=params,
        )
        return ccxt_processor.ohlcv_to_dataframe(data)

    async def close(self):
        """Close websocket connections"""
        await self.exchange.close()
