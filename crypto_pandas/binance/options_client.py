from dataclasses import dataclass, field

import pandas as pd
from typing import Any, Dict, Union
import grequests
import requests

from pandas import DataFrame

from crypto_pandas.binance.preprocessing import (
    preprocess_dict_binance,
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
            request_args["params"] = prepare_and_sign_parameters(
                secret=self.secret, params=params
            )
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

    def get_24hr_ticker_price_change_statistics(
        self,
        symbol: str,
    ) -> DataFrame:
        """
        24-hour rolling window price change statistics.

        :param symbol: Option trading pair, e.g BTC-200730-9000-C.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/exerciseHistory",
            params={
                "symbol": symbol,
            },
        )
        return response_to_dataframe(data)

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

    def get_historical_exercise_records(
        self,
        underlying: str = None,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
        limit: int = None,
    ) -> DataFrame:
        """
        Get historical exercise records.

        REALISTIC_VALUE_STRICKEN -> Exercised
        EXTRINSIC_VALUE_EXPIRED -> Expired OTM

        :param underlying: underlying asset, e.g ETH/BTC
        :param startTime: Start Time
        :param endTime: End Time
        :param limit: 	Number of result sets returned Default:100 Max:1000
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/exerciseHistory",
            params={
                "underlying": underlying,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
        )
        return response_to_dataframe(data)

    def get_open_interest(
        self,
        underlying: str,
        expiration: str,
    ) -> DataFrame:
        """
        Get recent market trades

        :param underlying: underlying asset, e.g ETH/BTC
        :param expiration: expiration date, e.g 221225
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/expiration",
            params={
                "underlying": underlying,
                "expiration": expiration,
            },
        )
        return response_to_dataframe(data)

    def get_recent_trades_list(
        self,
        symbol: str = None,
        limit: int = None,
    ) -> DataFrame:
        """
        Get recent market trades

        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :param limit: 	Number of result sets returned Default:100 Max:1500
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/openInterest",
            params={
                "symbol": symbol,
                "limit": limit,
            },
        )
        return response_to_dataframe(data)

    def get_recent_block_trades(
        self,
        symbol: str = None,
        limit: int = None,
    ) -> DataFrame:
        """
        Get recent block trades

        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :param limit: 	Number of result sets returned Default:100 Max:1500
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/blockTrades",
            params={
                "symbol": symbol,
                "limit": limit,
            },
        )
        return response_to_dataframe(data)

    def get_symbol_price_ticker(
        self,
        underlying: str,
    ) -> dict:
        """
        Get spot index price for option underlying.

        :param underlying: Spot pair (Option contract underlying asset, e.g BTCUSDT)
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/index",
            params={
                "underlying": underlying,
            },
        )
        return preprocess_dict_binance(data)

    def get_klines(
        self,
        symbol: str = None,
        interval: str = None,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
        limit: int = None,
    ) -> DataFrame:
        """
        Kline/candlestick bars for an option symbol. Klines are uniquely identified by their open time.

        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :param interval: Time interval
        :param startTime: Start Time
        :param endTime: End Time
        :param limit: 	Number of result sets returned Default:100 Max:1500
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/klines",
            params={
                "symbol": symbol,
                "interval": interval,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
        )
        return response_to_dataframe(data)

    def get_historical_trades(
        self,
        symbol: str = None,
        fromId: str = None,
        limit: int = 500,
    ) -> DataFrame:
        """
        Get older market historical trades.

        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :param fromId: The UniqueId ID from which to return. The latest deal record is returned by default.
        :param limit: 	Number of result sets returned Default:100 Max:1000
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/historicalTrades",
            params={
                "symbol": symbol,
                "fromId": fromId,
                "limit": limit,
            },
        )
        return response_to_dataframe(data)

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

    def get_account_info(
        self,
    ) -> DataFrame:
        """
        Get current account information.

        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/account",
            requires_auth=True,
        )
        return response_to_dataframe(data)

    def get_account_funding_flow(
        self,
        currency: str = None,
        recordId: int = None,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
        limit: int = 1000,
    ) -> DataFrame:
        """
        Query account funding flows.

        :param currency: Asset type, only support USDT as of now
        :param recordId: Return the recordId and subsequent data, the latest data is returned by default, e.g 100000
        :param startTime: Start Time
        :param endTime: End Time
        :param limit: Number of result sets returned Default:100 Max:1000
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/bill",
            params={
                "currency": currency,
                "recordId": recordId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            requires_auth=True,
        )
        return response_to_dataframe(data)

    def get_option_transaction_history_download_link_by_id(
        self, downloadId: str
    ) -> dict:
        """
        Get option transaction history download Link by Id
        :param downloadId: get by download id api
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/income/asyn/id",
            params={"downloadId": downloadId},
            requires_auth=True,
        )
        return preprocess_dict_binance(data)

    def post_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        timeInForce: str = "GTC",
        reduceOnly: bool = None,
        postOnly: bool = False,
        newOrderRespType: str = None,
        clientOrderId: str = None,
        isMmp: str = None,
    ) -> Dict[str, Any]:
        """
        Test Connectivity.
        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :param side: direction: SELL, BUY
        :param quantity: Order Quantity
        :param price: Order Price
        :param timeInForce: Time in force method（Default GTC）
        :param reduceOnly: Reduce Only（Default false）
        :param postOnly: Post Only（Default false）
        :param newOrderRespType: "ACK", "RESULT", Default "ACK"
        :param clientOrderId: User-defined order ID cannot be repeated in pending orders
        :param isMmp: Is market maker protection order, true/false

        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            path="eapi/v1/order",
            method="POST",
            params={
                "symbol": symbol,
                "side": side,
                "type": "LIMIT",
                "quantity": quantity,
                "price": price,
                "timeInForce": timeInForce,
                "reduceOnly": reduceOnly,
                "postOnly": postOnly,
                "newOrderRespType": newOrderRespType,
                "clientOrderId": clientOrderId,
                "isMmp": isMmp,
            },
            requires_auth=True,
        )

    def post_batch_orders(self, orders: pd.DataFrame) -> DataFrame:
        """
        Test Connectivity.
        :param orders: Pandas DataFrame of orders.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        orders = {"orders": options_orders_to_dict(orders)}
        data = self._request(
            path="eapi/v1/batchOrders", method="POST", params=orders, requires_auth=True
        )
        return response_to_dataframe(data)

    def delete_options_order(
        self, symbol: str, orderId: list = None, clientOrderId: list = None
    ) -> Dict[str, Any]:
        """
        Delete all orders by underlying.
        :param symbol: Underlying asset of orders.
        :param orderId: orderIds.
        :param clientOrderId: clientOrderIds.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            path="eapi/v1/batchOrders",
            method="DELETE",
            params={
                "symbol": symbol,
                "orderId": orderId,
                "clientOrderId": clientOrderId,
            },
            requires_auth=True,
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

    def get_single_order(
        self,
        symbol: str = None,
        orderId: str = None,
        limit: int = None,
    ) -> DataFrame:
        """
        Check an order status.

        These orders will not be found:
        order status is CANCELED or REJECTED, AND
        order has NO filled trade, AND
        created time + 3 days < current time

        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :param orderId: Returns the orderId and subsequent orders, the most recent order is returned by default.
        :param limit: 	Number of result sets returned Default:100 Max:1000
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/order",
            params={
                "symbol": symbol,
                "orderId": orderId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            requires_auth=True,
        )
        return response_to_dataframe(data)

    def get_option_order_history(
        self,
        symbol: str = None,
        orderId: str = None,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
        limit: int = None,
    ) -> DataFrame:
        """
        Query all finished orders within 5 days, finished status: CANCELLED FILLED REJECTED.

        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :param orderId: Returns the orderId and subsequent orders, the most recent order is returned by default.
        :param startTime: Start Time
        :param endTime: End Time
        :param limit: 	Number of result sets returned Default:100 Max:1000
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/historyOrders",
            params={
                "symbol": symbol,
                "orderId": orderId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            requires_auth=True,
        )
        return response_to_dataframe(data)

    def get_current_open_option_orders(
        self,
        symbol: str = None,
        orderId: str = None,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
        limit: int = None,
    ) -> DataFrame:
        """
        Query current all open orders, status: ACCEPTED PARTIALLY_FILLED.

        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :param orderId: Returns the orderId and subsequent orders, the most recent order is returned by default.
        :param startTime: Start Time
        :param endTime: End Time
        :param limit: 	Number of result sets returned Default:100 Max:1000
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/openOrders",
            params={
                "symbol": symbol,
                "orderId": orderId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            requires_auth=True,
        )
        return response_to_dataframe(data)

    def get_position(self, symbol: str) -> DataFrame:
        """
        Get current position information.
        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/position",
            params={"symbol": symbol},
            requires_auth=True,
        )
        return response_to_dataframe(data)
