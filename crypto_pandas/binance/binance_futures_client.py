import pandas as pd
from pydantic import BaseModel, Field, SecretStr
from typing import Any, Dict, Union
import requests

from crypto_pandas.binance.binance_pandas import (
    response_to_dataframe,
    response_to_dict,
)
from crypto_pandas.binance.binance_requests import prepare_requests_parameters
from crypto_pandas.binance.column_names import klines_column_names


class BinanceFuturesClient(BaseModel):
    """
    A client for interacting with the Binance Futures API.

    :param env: The API env (`prod` or `paper`).
    :param api_key: The API Key for authentication.
    """

    env: str = Field(default="paper", description="The API env (`prod` or `paper`)")
    api_key: SecretStr = Field(
        default=None, description="The API Key for authentication"
    )

    @property
    def base_url(self) -> str:
        return (
            "https://fapi.binance.com"
            if self.env == "prod"
            else "https://testnet.binancefuture.com"
        )

    def _request(
        self,
        method: str,
        path: str,
        params: Dict[str, Any] = None,
        body: Dict[str, Any] = None,
        column_names: list = None,
    ) -> Union[str, Dict[str, Any], pd.DataFrame]:
        """
        Internal method to make API requests.

        :param method: HTTP method (e.g., GET, POST, PUT, DELETE).
        :param path: Path of the API endpoint.
        :param params: Query parameters for the request.
        :param body: Request body for POST/PUT methods.
        :param body: Potential column names to use in dataframe.
        :return: The JSON response from the API.
        """
        request_args = {
            "method": method,
            "url": f"{self.base_url}{path}",
        }
        if self.api_key:
            request_args["headers"] = {"Authorization": f"Bearer {self.api_key}"}
        if params is not None:
            request_args["params"] = prepare_requests_parameters(params)
        if body is not None:
            request_args["json"] = body
        response = requests.request(**request_args)
        response.raise_for_status()
        try:
            data = response.json()
            if isinstance(data, list):
                data = response_to_dataframe(data, column_names=column_names)
            if isinstance(data, dict):
                data = response_to_dict(data)
            return data
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("Something Else:", err)

    @property
    def info(self) -> Dict[str, str]:
        """
        Return API information.

        :returns: A dictionary containing the API title, description, and version.
        """
        return {
            "title": "Binance Futures API",
            "description": """Comprehensive API documentation for Binance Futures endpoints.""",
            "version": "1.0.0",
        }

    def get_fapi_ping(
        self,
    ) -> Dict[str, Any]:
        """
        Test Connectivity.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/fapi/v1/ping",
        )

    def get_fapi_time(
        self,
    ) -> Dict[str, Any]:
        """
        Check Server Time.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/fapi/v1/time",
        )

    def get_fapi_exchange_info(
        self,
    ) -> Dict[str, Any]:
        """
        Exchange Information.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/fapi/v1/exchangeInfo",
        )

    def get_fapi_depth(
        self,
        symbol: str,
        limit: int = None,
    ) -> Dict[str, Any]:
        """
        Get Orderbook
        Parameters:
        :param symbol: Trading symbol.
            Type: str
        :param limit: Limit the number of results. Default is 500.
            Type:int.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/fapi/v1/depth",
            params={
                "symbol": symbol,
                "limit": limit,
            },
        )

    def get_fapi_trades(
        self,
        symbol: str,
        limit: int = None,
    ) -> Dict[str, Any]:
        """
        Recent Market Trades
        Parameters:
        :param symbol: Trading symbol.
            Type: str
        :param limit: Limit the number of results. Default is 500, max is 1000.
            Type:int.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/fapi/v1/trades",
            params={
                "symbol": symbol,
                "limit": limit,
            },
        )

    def get_fapi_historical_trades(
        self,
        symbol: str,
        limit: int = None,
        fromId: int = None,
    ) -> Dict[str, Any]:
        """
        Old Trade Lookup
        Parameters:
        :param symbol: Trading symbol.
            Type: str
        :param limit: Limit the number of results. Default is 500, max is 1000.
            Type:int
        :param fromId: Trade ID to fetch from.
            Type:int.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/fapi/v1/historicalTrades",
            params={
                "symbol": symbol,
                "limit": limit,
                "fromId": fromId,
            },
        )

    def get_fapi_agg_trades(
        self,
        symbol: str,
        limit: int = None,
        fromId: int = None,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
    ) -> Dict[str, Any]:
        """
        Compressed/Aggregate Trades
        Parameters:
        :param symbol: Trading symbol.
            Type: str
        :param limit: Limit the number of results. Default is 500, max is 1000.
            Type:int
        :param fromId: Aggregate trade ID to fetch from.
            Type:int
        :param startTime: Start time in milliseconds.
            Type:int
        :param endTime: End time in milliseconds.
            Type:int.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/fapi/v1/aggTrades",
            params={
                "symbol": symbol,
                "limit": limit,
                "fromId": fromId,
                "startTime": startTime,
                "endTime": endTime,
            },
        )

    def get_fapi_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = None,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
    ) -> Dict[str, Any]:
        """
        Kline/Candlestick Data
        Parameters:
        :param symbol: Trading symbol.
            Type: str
        :param interval: Kline interval (e.g., 1m, 5m, 1h, 1d).
            Type: str
        :param limit: Limit the number of results. Default is 500, max is 1000.
            Type:int
        :param startTime: Start time in milliseconds.
            Type:int
        :param endTime: End time in milliseconds.
            Type:int.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/fapi/v1/klines",
            params={
                "symbol": symbol,
                "interval": interval,
                "limit": limit,
                "startTime": startTime,
                "endTime": endTime,
            },
            column_names=klines_column_names,
        )

    def get_fapi_mark_price(
        self,
        symbol: str = None,
    ) -> Dict[str, Any]:
        """
        Mark Price and Funding Rate
        Parameters:
        :param symbol: Trading symbol.
            Type: str.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/fapi/v1/markPrice",
            params={
                "symbol": symbol,
            },
        )

    def get_fapi_funding_rate(
        self,
        symbol: str,
        limit: int = None,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
    ) -> Dict[str, Any]:
        """
        Funding Rate History
        Parameters:
        :param symbol: Trading symbol.
            Type: str
        :param limit: Limit the number of results. Default is 500, max is 1000.
            Type:int
        :param startTime: Start time in milliseconds.
            Type:int
        :param endTime: End time in milliseconds.
            Type:int.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/fapi/v1/fundingRate",
            params={
                "symbol": symbol,
                "limit": limit,
                "startTime": startTime,
                "endTime": endTime,
            },
        )

    def get_fapi_ticker__24hr(
        self,
        symbol: str = None,
    ) -> Dict[str, Any]:
        """
        24-Hour Ticker Price Change
        Parameters:
        :param symbol: Trading symbol. If not sent, returns data for all symbols.
            Type: str.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/fapi/v1/ticker/24hr",
            params={
                "symbol": symbol,
            },
        )

    def get_fapi_ticker_price(
        self,
        symbol: str = None,
    ) -> Dict[str, Any]:
        """
        Symbol Price Ticker
        Parameters:
        :param symbol: Trading symbol. If not sent, returns data for all symbols.
            Type: str.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/fapi/v2/ticker/price",
            params={
                "symbol": symbol,
            },
        )

    def get_fapi_ticker_book_ticker(
        self,
        symbol: str = None,
    ) -> Dict[str, Any]:
        """
        Order Book Best Price/Quantity
        Parameters:
        :param symbol: Trading symbol. If not sent, returns data for all symbols.
            Type: str.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/fapi/v1/ticker/bookTicker",
            params={
                "symbol": symbol,
            },
        )
