from dataclasses import dataclass, field

import pandas as pd
from typing import Any, Dict, Union
import grequests
import requests

from crypto_pandas.binance.preprocessing import (
    preprocess_dict_binance,
    response_to_dataframe_binance,
)
from crypto_pandas.binance.markets import (
    exchange_info_to_dataframe,
    depth_to_dataframe,
)
from crypto_pandas.binance.orders import (
    options_orders_to_dict,
)
from crypto_pandas.binance.requests import (
    prepare_and_sign_parameters,
)


@dataclass
class BinanceOptionsClient:
    """
    A client for interacting with the Binance Options API.

    :param api_key: The API Key for authentication.
    :param secret: The API secret for authentication.
    """

    api_key: str = field(default=None, repr=False)
    secret: str = field(default=None, repr=False)

    def _request(
        self,
        path: str,
        method: str = "GET",
        params: Dict[str, Any] = None,
        requires_auth: bool = False,
    ) -> Union[list, dict, requests.Response]:
        """
        Internal method to make API requests.

        :param method: HTTP method (e.g., GET, POST, PUT, DELETE).
        :param path: Path of the API endpoint.
        :param params: Query parameters for the request.
        :param requires_auth: If the endpoint requires authentication.
        :return: The JSON response from the API.
        """
        request_args: Dict[str, Any] = {
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
        if response.status_code == 200:
            if "x-mbx-used-weight-1m" in response.headers:
                self.used_weight_1m = int(response.headers.get("x-mbx-used-weight-1m"))
            return response.json()
        else:
            response.raise_for_status()

    def get_server_time(
        self,
    ) -> dict:
        """
        Test connectivity to the Rest API and get the current server time.

        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(path="eapi/v1/time")
        return preprocess_dict_binance(data)

    def get_24hr_ticker_price_change_statistics(
        self,
        symbol: str = None,
    ) -> pd.DataFrame:
        """
        24-hour rolling window price change statistics.

        :param symbol: Option trading pair, e.g BTC-200730-9000-C.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/ticker",
            params={
                "symbol": symbol,
            },
        )
        return response_to_dataframe_binance(data)

    def get_exchange_info(
        self,
    ) -> pd.DataFrame:
        """
        Get exchange info.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/exchangeInfo",
        )
        return exchange_info_to_dataframe(data, record_path="optionSymbols")

    def get_historical_exercise_records(
        self,
        underlying: str = None,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
        limit: int = None,
    ) -> pd.DataFrame:
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
        return response_to_dataframe_binance(data)

    def get_open_interest(
        self,
        underlyingAsset: str,
        expiration: Union[str, pd.Timestamp],
    ) -> pd.DataFrame:
        """
        Get recent market trades

        :param underlyingAsset: underlying asset, e.g ETH/BTC
        :param expiration: expiration date, e.g 221225
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        if not isinstance(expiration, str):
            expiration = expiration.strftime("%y%m%d")
        data = self._request(
            path="eapi/v1/openInterest",
            params={
                "underlyingAsset": underlyingAsset,
                "expiration": expiration,
            },
        )
        return response_to_dataframe_binance(data)

    def get_order_book(
        self,
        symbol: str,
        limit: int = None,
    ) -> pd.DataFrame:
        """
        Check orderbook depth on specific symbol

        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :param limit: Default:100 Max:1000.Optional value:[10, 20, 50, 100, 500, 1000]
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/depth",
            params={
                "symbol": symbol,
                "limit": limit,
            },
        )
        return depth_to_dataframe(data)

    def get_recent_trades_list(
        self,
        symbol: str,
        limit: int = None,
    ) -> pd.DataFrame:
        """
        Get recent market trades

        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :param limit: 	Number of result sets returned Default:100 Max:1500
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/trades",
            params={
                "symbol": symbol,
                "limit": limit,
            },
        )
        return response_to_dataframe_binance(data)

    def get_recent_block_trades(
        self,
        symbol: str = None,
        limit: int = None,
    ) -> pd.DataFrame:
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
        return response_to_dataframe_binance(data)

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
        symbol: str,
        interval: str,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
        limit: int = None,
    ) -> pd.DataFrame:
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
        return response_to_dataframe_binance(data)

    def get_historical_trades(
        self,
        symbol: str = None,
        fromId: str = None,
        limit: int = 500,
    ) -> pd.DataFrame:
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
        return response_to_dataframe_binance(data)

    def get_mark(self, symbol: str = None) -> pd.DataFrame:
        """
        Get mark data.

        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(path="eapi/v1/mark", params={"symbol": symbol})
        return response_to_dataframe_binance(data)

    def get_account_info(
        self,
    ) -> dict:
        """
        Get current account information.

        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/account",
            requires_auth=True,
        )
        data["asset"] = response_to_dataframe_binance(data["asset"])
        data["greek"] = response_to_dataframe_binance(data["greek"])
        return preprocess_dict_binance(data)

    def get_account_funding_flow(
        self,
        currency: str = "USDT",
        recordId: int = None,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
        limit: int = None,
    ) -> pd.DataFrame:
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
        return response_to_dataframe_binance(data)

    def get_download_id_for_option_transaction_history(
        self,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
    ) -> dict:
        """
        Get download id for option transaction history
        :param startTime: Start Time
        :param endTime: End Time
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/income/asyn",
            params={
                "startTime": startTime,
                "endTime": endTime,
            },
            requires_auth=True,
        )
        return preprocess_dict_binance(data)

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
        Send a new order.
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

    def post_batch_orders(self, orders: pd.DataFrame) -> pd.DataFrame:
        """
        Send multiple option orders.
        :param orders: Pandas DataFrame of orders.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/batchOrders",
            method="POST",
            params={"orders": options_orders_to_dict(orders)},
            requires_auth=True,
        )
        return response_to_dataframe_binance(data)

    def delete_options_order(
        self, symbol: str, orderId: list = None, clientOrderId: list = None
    ) -> Dict[str, Any]:
        """
        Cancel an active order.
        :param symbol: Underlying asset of orders.
        :param orderId: orderIds.
        :param clientOrderId: clientOrderIds.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/order",
            method="DELETE",
            params={
                "symbol": symbol,
                "orderId": orderId,
                "clientOrderId": clientOrderId,
            },
            requires_auth=True,
        )
        return preprocess_dict_binance(data)

    def delete_multiple_options_orders(
        self, symbol: str, orderIds: list = None, clientOrderIds: list = None
    ) -> pd.DataFrame:
        """
        Delete all orders by underlying.
        :param symbol: Underlying asset of orders.
        :param orderIds: orderIds.
        :param clientOrderIds: clientOrderIds.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/batchOrders",
            method="DELETE",
            params={
                "symbol": symbol,
                "orderIds": orderIds,
                "clientOrderIds": clientOrderIds,
            },
            requires_auth=True,
        )
        return response_to_dataframe_binance(data)

    def delete_all_options_orders_by_underlying(self, underlying: str) -> dict:
        """
        Delete all orders by underlying.
        :param underlying: Underlying asset of orders.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/allOpenOrdersByUnderlying",
            method="DELETE",
            params={"underlying": underlying},
            requires_auth=True,
        )
        return data

    def delete_all_options_orders_on_symbol(self, symbol: str) -> dict:
        """
        Delete all orders by underlying.
        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/allOpenOrders",
            method="DELETE",
            params={"symbol": symbol},
            requires_auth=True,
        )
        return data

    def get_single_order(
        self,
        symbol: str = None,
        orderId: str = None,
        limit: int = None,
    ) -> pd.DataFrame:
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
        return response_to_dataframe_binance(data)

    def get_option_order_history(
        self,
        symbol: str,
        orderId: str = None,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
        limit: int = None,
    ) -> pd.DataFrame:
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
        return response_to_dataframe_binance(data)

    def get_current_open_option_orders(
        self,
        symbol: str = None,
        orderId: str = None,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
        limit: int = None,
    ) -> pd.DataFrame:
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
        return response_to_dataframe_binance(data)

    def get_position(self, symbol: Union[str, list] = None) -> pd.DataFrame:
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
        return response_to_dataframe_binance(data)

    def get_exercise_record(
        self,
        symbol: str = None,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
        limit: int = None,
    ) -> pd.DataFrame:
        """
        Get account exercise records.
        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :param startTime: Start Time
        :param endTime: End Time
        :param limit: Number of result sets returned Default:100 Max:1000
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/exerciseRecord",
            params={
                "symbol": symbol,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            requires_auth=True,
        )
        return response_to_dataframe_binance(data)

    def get_account_trade_list(
        self,
        symbol: str = None,
        fromId: str = None,
        startTime: pd.Timestamp = None,
        endTime: pd.Timestamp = None,
        limit: int = None,
    ) -> pd.DataFrame:
        """
        Get trades for a specific account and symbol.
        :param symbol: Option trading pair, e.g BTC-200730-9000-C
        :param fromId: Trade id to fetch from. Default gets most recent trades, e.g 4611875134427365376
        :param startTime: Start Time
        :param endTime: End Time
        :param limit: Default:100 Max:1000
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            path="eapi/v1/userTrades",
            params={
                "symbol": symbol,
                "fromId": fromId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            requires_auth=True,
        )
        return response_to_dataframe_binance(data)
