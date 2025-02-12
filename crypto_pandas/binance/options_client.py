from dataclasses import dataclass, field

import pandas as pd
from typing import Any, Dict, Union
import grequests
import requests

from pandas import DataFrame

from crypto_pandas.binance.preprocessing import (
    preprocess_dataframe_binance,
    response_to_dataframe,
)
from crypto_pandas.binance.options import (
    options_orders_to_dict,
)


@dataclass
class BinanceOptionsClient:
    """
    A client for interacting with the Binance Options API.

    :param api_key: The API Key for authentication.
    :param secret: The API secret for authentication.
    """

    api_key: str = field(repr=False)
    secret: str = field(repr=False)

    def _request(
        self,
        path: str,
        method: str = "GET",
        params: Dict[str, Any] = None,
        requires_auth: bool = False,
    ) -> Union[list, dict]:
        """
        Internal method to make API requests.

        :param method: HTTP method (e.g., GET, POST, PUT, DELETE).
        :param path: Path of the API endpoint.
        :param params: Query parameters for the request.
        :param requires_auth: If the endpoint requires authentication.
        :return: The JSON response from the API.
        """
        request_args = {
            "url": f"https://eapi.binance.com/{path}",
            "method": method,
        }
        if requires_auth:
            request_args["params"] = prepare_and_sign_parameters(secret=self.secret, params=params)
            request_args["headers"] = {
                "X-MBX-APIKEY": self.api_key,
            }
        elif params:
            request_args["params"] = params
        response = requests.request(**request_args)
        response.raise_for_status()
        try:
            data = response.json()
            return data
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("Something Else:", err)

    def get_exchange_info(
        self,
    ) -> DataFrame:
        """
        Get exchange info.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/exchangeInfo",
        )
        data = pd.json_normalize(
            data=data,
            record_path=["optionSymbols"],
            meta=["timezone", "serverTime", "rateLimits"],
        )
        return preprocess_dataframe_binance(data)

    def get_mark(
        self,
    ) -> DataFrame:
        """
        Get mark data.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/mark",
        )
        return response_to_dataframe(data)

    def post_batch_orders(self, orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Test Connectivity.
        :param orders: Pandas DataFrame of orders.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        orders = {"orders": options_orders_to_dict(orders)}
        return self._request(
            path="eapi/v1/batchOrders", method="POST", params=orders, requires_auth=True
        )

    def delete_multiple_options_orders(
        self, symbol: str, orderIds: list = None, clientOrderIds: list = None
    ) -> Dict[str, Any]:
        """
        Delete all orders by underlying.
        :param symbol: Underlying asset of orders.
        :param orderIds: orderIds.
        :param clientOrderIds: clientOrderIds.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            path="eapi/v1/batchOrders",
            method="DELETE",
            params={
                "symbol": symbol,
                "orderIds": orderIds,
                "clientOrderIds": clientOrderIds,
            },
            requires_auth=True,
        )

    def delete_all_options_orders_by_underlying(
        self, underlying: str
    ) -> Dict[str, Any]:
        """
        Delete all orders by underlying.
        :param underlying: Underlying asset of orders.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            path="eapi/v1/allOpenOrdersByUnderlying",
            method="DELETE",
            params={"underlying": underlying},
            requires_auth=True,
        )

    def delete_all_options_orders_on_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        Delete all orders by underlying.
        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            path="eapi/v1/allOpenOrders",
            method="DELETE",
            params={"symbol": symbol},
            requires_auth=True,
        )
