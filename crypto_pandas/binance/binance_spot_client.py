import pandas as pd
from pydantic import BaseModel, Field, SecretStr
from typing import Any, Dict, List, Union
import requests

from crypto_pandas.binance.binance_pandas import (
    binance_response_to_dataframe,
    binance_response_to_dict,
)
from crypto_pandas.binance.binance_requests import prepare_requests_parameters
from crypto_pandas.binance.column_names import klines_column_names


class BinanceSpotClient(BaseModel):
    """
    A client for interacting with the Binance Spot API.

    :param env: The API env (`prod` or `paper`).
    :param api_key: The API Key for authentication.
    """

    env: str = Field(default="paper", description="The API Key for authentication")
    api_key: SecretStr = Field(
        default=None, description="The API Key for authentication"
    )

    @property
    def base_url(self) -> str:
        return (
            "https://api.binance.com/"
            if self.env == "prod"
            else "https://testnet.binance.vision/"
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
                data = binance_response_to_dataframe(data, column_names=column_names)
            if isinstance(data, dict):
                data = binance_response_to_dict(data)
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
            "title": "Binance Public Spot API",
            "description": """OpenAPI Specifications for the Binance Public Spot API

API documents:
  - [https://github.com/binance/binance-spot-api-docs](https://github.com/binance/binance-spot-api-docs)
  - [https://binance-docs.github.io/apidocs/spot/en](https://binance-docs.github.io/apidocs/spot/en)""",
            "version": "1.0",
        }

    def get_api_ping(
        self,
    ) -> Dict[str, Any]:
        """
        Test Connectivity.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/ping",
        )

    def get_api_time(
        self,
    ) -> Dict[str, Any]:
        """
        Check Server Time.
        :returns: Binance server UTC timestamp
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/time",
        )

    def get_api_exchange_info(
        self,
        optionalSymbol: str = None,
        arraySymbols: str = None,
        permissions: str = None,
    ) -> Dict[str, Any]:
        """
        Exchange Information
        Parameters:
        :param optionalSymbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param arraySymbols:
            Type: str
        :param permissions:
            Type: str.
        :returns: Current exchange trading rules and symbol information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/exchangeInfo",
            params={
                "optionalSymbol": optionalSymbol,
                "arraySymbols": arraySymbols,
                "permissions": permissions,
            },
        )

    def get_api_depth(
        self,
        symbol: str,
        limit: int = None,
    ) -> Dict[str, Any]:
        """
        Order Book
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param limit: If limit > 5000, then the response will truncate to 5000
            Type:int.
        :returns: Order book
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/depth",
            params={
                "symbol": symbol,
                "limit": limit,
            },
        )

    def get_api_trades(
        self,
        symbol: str,
        limit: int = None,
    ) -> Dict[str, Any]:
        """
        Recent Trades List
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param limit: Default 500; max 1000.
            Type: int.
        :returns: Trade list
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/trades",
            params={
                "symbol": symbol,
                "limit": limit,
            },
        )

    def get_api_historical_trades(
        self,
        symbol: str,
        limit: int = None,
        fromId: int = None,
    ) -> Dict[str, Any]:
        """
        Old Trade Lookup
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param limit: Default 500; max 1000.
            Type: int
        :param fromId: Trade id to fetch from. Default gets most recent trades.
            Type: int.
        :returns: Trade list
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/historicalTrades",
            params={
                "symbol": symbol,
                "limit": limit,
                "fromId": fromId,
            },
        )

    def get_api_agg_trades(
        self,
        symbol: str,
        fromId: int = None,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """
        Compressed/Aggregate Trades List
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param fromId: Trade id to fetch from. Default gets most recent trades.
            Type: int
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param limit: Default 500; max 1000.
            Type: int.
        :returns: Trade list
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/aggTrades",
            params={
                "symbol": symbol,
                "fromId": fromId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
        )

    def get_api_klines(
        self,
        symbol: str,
        interval: str,
        startTime: int = None,
        endTime: int = None,
        timeZone: str = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """
        Kline/Candlestick Data
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param interval: kline intervals
            Type:str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param timeZone: Default: 0 (UTC)
            Type:str
        :param limit: Default 500; max 1000.
            Type: int.
        :returns: Kline data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/klines",
            params={
                "symbol": symbol,
                "interval": interval,
                "startTime": startTime,
                "endTime": endTime,
                "timeZone": timeZone,
                "limit": limit,
            },
            column_names=klines_column_names,
        )

    def get_api_ui_klines(
        self,
        symbol: str,
        interval: str,
        startTime: int = None,
        endTime: int = None,
        timeZone: str = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """
        UIKlines
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param interval: kline intervals
            Type:str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param timeZone: Default: 0 (UTC)
            Type:str
        :param limit: Default 500; max 1000.
            Type: int.
        :returns: UIKline data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/uiKlines",
            params={
                "symbol": symbol,
                "interval": interval,
                "startTime": startTime,
                "endTime": endTime,
                "timeZone": timeZone,
                "limit": limit,
            },
            column_names=klines_column_names,
        )

    def get_api_avg_price(
        self,
        symbol: str,
    ) -> Dict[str, Any]:
        """
        Current Average Price
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str.
        :returns: Average price
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/avgPrice",
            params={
                "symbol": symbol,
            },
        )

    def get_api_ticker__24hr(
        self,
        optionalSymbol: str = None,
        arraySymbols: str = None,
        tickerType: str = None,
    ) -> Dict[str, Any]:
        """
                24hr Ticker Price Change Statistics
                Parameters:
                :param optionalSymbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param arraySymbols:
                    Type: str
                :param tickerType: Supported values: FULL or MINI.
        If none provided, the default is FULL
                    Type: str.
                :returns: 24hr ticker
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/ticker/24hr",
            params={
                "optionalSymbol": optionalSymbol,
                "arraySymbols": arraySymbols,
                "tickerType": tickerType,
            },
        )

    def get_api_ticker_trading_day(
        self,
        optionalSymbol: str = None,
        arraySymbols: str = None,
        timeZone: str = None,
        tickerType: str = None,
    ) -> Dict[str, Any]:
        """
                Trading Day Ticker
                Parameters:
                :param optionalSymbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param arraySymbols:
                    Type: str
                :param timeZone: Default: 0 (UTC)
                    Type:str
                :param tickerType: Supported values: FULL or MINI.
        If none provided, the default is FULL
                    Type: str.
                :returns: Trading day ticker
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/ticker/tradingDay",
            params={
                "optionalSymbol": optionalSymbol,
                "arraySymbols": arraySymbols,
                "timeZone": timeZone,
                "tickerType": tickerType,
            },
        )

    def get_api_ticker_price(
        self,
        optionalSymbol: str = None,
        arraySymbols: str = None,
    ) -> Dict[str, Any]:
        """
        Symbol Price Ticker
        Parameters:
        :param optionalSymbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param arraySymbols:
            Type: str.
        :returns: Price ticker
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/ticker/price",
            params={
                "optionalSymbol": optionalSymbol,
                "arraySymbols": arraySymbols,
            },
        )

    def get_api_ticker_book_ticker(
        self,
        optionalSymbol: str = None,
        arraySymbols: str = None,
    ) -> Dict[str, Any]:
        """
        Symbol Order Book Ticker
        Parameters:
        :param optionalSymbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param arraySymbols:
            Type: str.
        :returns: Order book ticker
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/ticker/bookTicker",
            params={
                "optionalSymbol": optionalSymbol,
                "arraySymbols": arraySymbols,
            },
        )

    def get_api_ticker(
        self,
        optionalSymbol: str = None,
        arraySymbols: str = None,
        windowSize: str = None,
        type_: str = None,
    ) -> Dict[str, Any]:
        """
                Rolling window price change statistics
                Parameters:
                :param optionalSymbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param arraySymbols:
                    Type: str
                :param windowSize: Defaults to 1d if no parameter provided.
        Supported windowSize values:
        1m,2m....59m for minutes
        1h, 2h....23h - for hours
        1d...7d - for days.

        Units cannot be combined (e.g. 1d2h is not allowed)
                    Type:str
                :param type_: Supported values: FULL or MINI.
        If none provided, the default is FULL
                    Type:str.
                :returns: Rolling price ticker
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/ticker",
            params={
                "optionalSymbol": optionalSymbol,
                "arraySymbols": arraySymbols,
                "windowSize": windowSize,
                "type": type_,
            },
        )

    def post_api_order_test(
        self,
        symbol: str,
        side: str,
        orderType: str,
        timestamp: int,
        signature: str,
        timeInForce: str = None,
        optionalQuantity: float = None,
        quoteOrderQty: float = None,
        optionalPrice: float = None,
        newClientOrderId: str = None,
        strategyId: int = None,
        strategyType: int = None,
        stopPrice: float = None,
        optionalTrailingDelta: float = None,
        icebergQty: float = None,
        newOrderRespType: str = None,
        recvWindow: int = None,
        computeCommissionRates: bool = None,
    ) -> Dict[str, Any]:
        """
        Test New Order (TRADE)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param side:
            Type: str
        :param orderType: Order type
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param timeInForce: Order time in force
            Type: str
        :param optionalQuantity: Order quantity
            Type: float
        :param quoteOrderQty: Quote quantity
            Type: float
        :param optionalPrice: Order price
            Type: float
        :param newClientOrderId: Used to uniquely identify this cancel. Automatically generated by default
            Type: str
        :param strategyId:
            Type: int
        :param strategyType: The value cannot be less than 1000000.
            Type: int
        :param stopPrice: Used with STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, and TAKE_PROFIT_LIMIT orders.
            Type: float
        :param optionalTrailingDelta: Used with STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, and TAKE_PROFIT_LIMIT orders.
            Type: float
        :param icebergQty: Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
            Type: float
        :param newOrderRespType: Set the response JSON. MARKET and LIMIT order types default to FULL, all other orders default to ACK.
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int
        :param computeCommissionRates: Default: false
            Type:bool.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/api/v3/order/test",
            params={
                "symbol": symbol,
                "side": side,
                "orderType": orderType,
                "timestamp": timestamp,
                "signature": signature,
                "timeInForce": timeInForce,
                "optionalQuantity": optionalQuantity,
                "quoteOrderQty": quoteOrderQty,
                "optionalPrice": optionalPrice,
                "newClientOrderId": newClientOrderId,
                "strategyId": strategyId,
                "strategyType": strategyType,
                "stopPrice": stopPrice,
                "optionalTrailingDelta": optionalTrailingDelta,
                "icebergQty": icebergQty,
                "newOrderRespType": newOrderRespType,
                "recvWindow": recvWindow,
                "computeCommissionRates": computeCommissionRates,
            },
        )

    def get_api_order(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        orderId: int = None,
        origClientOrderId: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Order (USER_DATA)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: Order id
            Type: int
        :param origClientOrderId: Order id from client
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Order details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/order",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "origClientOrderId": origClientOrderId,
                "recvWindow": recvWindow,
            },
        )

    def post_api_order(
        self,
        symbol: str,
        side: str,
        orderType: str,
        timestamp: int,
        signature: str,
        timeInForce: str = None,
        optionalQuantity: float = None,
        quoteOrderQty: float = None,
        optionalPrice: float = None,
        newClientOrderId: str = None,
        strategyId: int = None,
        strategyType: int = None,
        stopPrice: float = None,
        optionalTrailingDelta: float = None,
        icebergQty: float = None,
        newOrderRespType: str = None,
        selfTradePreventionMode: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        New Order (TRADE)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param side:
            Type: str
        :param orderType: Order type
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param timeInForce: Order time in force
            Type: str
        :param optionalQuantity: Order quantity
            Type: float
        :param quoteOrderQty: Quote quantity
            Type: float
        :param optionalPrice: Order price
            Type: float
        :param newClientOrderId: Used to uniquely identify this cancel. Automatically generated by default
            Type: str
        :param strategyId:
            Type: int
        :param strategyType: The value cannot be less than 1000000.
            Type: int
        :param stopPrice: Used with STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, and TAKE_PROFIT_LIMIT orders.
            Type: float
        :param optionalTrailingDelta: Used with STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, and TAKE_PROFIT_LIMIT orders.
            Type: float
        :param icebergQty: Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
            Type: float
        :param newOrderRespType: Set the response JSON. MARKET and LIMIT order types default to FULL, all other orders default to ACK.
            Type: str
        :param selfTradePreventionMode: The allowed enums is dependent on what is configured on the symbol. The possible supported values are EXPIRE_TAKER, EXPIRE_MAKER, EXPIRE_BOTH, NONE.
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Order result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/api/v3/order",
            params={
                "symbol": symbol,
                "side": side,
                "orderType": orderType,
                "timestamp": timestamp,
                "signature": signature,
                "timeInForce": timeInForce,
                "optionalQuantity": optionalQuantity,
                "quoteOrderQty": quoteOrderQty,
                "optionalPrice": optionalPrice,
                "newClientOrderId": newClientOrderId,
                "strategyId": strategyId,
                "strategyType": strategyType,
                "stopPrice": stopPrice,
                "optionalTrailingDelta": optionalTrailingDelta,
                "icebergQty": icebergQty,
                "newOrderRespType": newOrderRespType,
                "selfTradePreventionMode": selfTradePreventionMode,
                "recvWindow": recvWindow,
            },
        )

    def delete_api_order(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        orderId: int = None,
        origClientOrderId: str = None,
        newClientOrderId: str = None,
        cancelRestrictions: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Cancel Order (TRADE)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: Order id
            Type: int
        :param origClientOrderId: Order id from client
            Type: str
        :param newClientOrderId: Used to uniquely identify this cancel. Automatically generated by default
            Type: str
        :param cancelRestrictions:
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Cancelled order
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="DELETE",
            path="/api/v3/order",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "origClientOrderId": origClientOrderId,
                "newClientOrderId": newClientOrderId,
                "cancelRestrictions": cancelRestrictions,
                "recvWindow": recvWindow,
            },
        )

    def post_api_order_cancel_replace(
        self,
        symbol: str,
        side: str,
        orderType: str,
        cancelReplaceMode: str,
        timestamp: int,
        signature: str,
        cancelRestrictions: str = None,
        timeInForce: str = None,
        optionalQuantity: float = None,
        quoteOrderQty: float = None,
        optionalPrice: float = None,
        cancelNewClientOrderId: str = None,
        cancelOrigClientOrderId: str = None,
        cancelOrderId: int = None,
        newClientOrderId: str = None,
        strategyId: int = None,
        strategyType: int = None,
        stopPrice: float = None,
        optionalTrailingDelta: float = None,
        icebergQty: float = None,
        newOrderRespType: str = None,
        selfTradePreventionMode: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Cancel an Existing Order and Send a New Order (Trade)
                Parameters:
                :param symbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param side:
                    Type: str
                :param orderType: Order type
                    Type: str
                :param cancelReplaceMode: - `STOP_ON_FAILURE` If the cancel request fails, the new order placement will not be attempted.
        - `ALLOW_FAILURES` If new order placement will be attempted even if cancel request fails.
                    Type:str
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param cancelRestrictions:
                    Type: str
                :param timeInForce: Order time in force
                    Type: str
                :param optionalQuantity: Order quantity
                    Type: float
                :param quoteOrderQty: Quote quantity
                    Type: float
                :param optionalPrice: Order price
                    Type: float
                :param cancelNewClientOrderId: Used to uniquely identify this cancel. Automatically generated by default
                    Type:str
                :param cancelOrigClientOrderId: Either the cancelOrigClientOrderId or cancelOrderId must be provided. If both are provided, cancelOrderId takes precedence.
                    Type:str
                :param cancelOrderId: Either the cancelOrigClientOrderId or cancelOrderId must be provided. If both are provided, cancelOrderId takes precedence.
                    Type:int
                :param newClientOrderId: Used to uniquely identify this cancel. Automatically generated by default
                    Type: str
                :param strategyId:
                    Type: int
                :param strategyType: The value cannot be less than 1000000.
                    Type: int
                :param stopPrice: Used with STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, and TAKE_PROFIT_LIMIT orders.
                    Type: float
                :param optionalTrailingDelta: Used with STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, and TAKE_PROFIT_LIMIT orders.
                    Type: float
                :param icebergQty: Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
                    Type: float
                :param newOrderRespType: Set the response JSON. MARKET and LIMIT order types default to FULL, all other orders default to ACK.
                    Type: str
                :param selfTradePreventionMode: The allowed enums is dependent on what is configured on the symbol. The possible supported values are EXPIRE_TAKER, EXPIRE_MAKER, EXPIRE_BOTH, NONE.
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Operation details
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/api/v3/order/cancelReplace",
            params={
                "symbol": symbol,
                "side": side,
                "orderType": orderType,
                "cancelReplaceMode": cancelReplaceMode,
                "timestamp": timestamp,
                "signature": signature,
                "cancelRestrictions": cancelRestrictions,
                "timeInForce": timeInForce,
                "optionalQuantity": optionalQuantity,
                "quoteOrderQty": quoteOrderQty,
                "optionalPrice": optionalPrice,
                "cancelNewClientOrderId": cancelNewClientOrderId,
                "cancelOrigClientOrderId": cancelOrigClientOrderId,
                "cancelOrderId": cancelOrderId,
                "newClientOrderId": newClientOrderId,
                "strategyId": strategyId,
                "strategyType": strategyType,
                "stopPrice": stopPrice,
                "optionalTrailingDelta": optionalTrailingDelta,
                "icebergQty": icebergQty,
                "newOrderRespType": newOrderRespType,
                "selfTradePreventionMode": selfTradePreventionMode,
                "recvWindow": recvWindow,
            },
        )

    def get_api_open_orders(
        self,
        timestamp: int,
        signature: str,
        optionalSymbol: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Current Open Orders (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalSymbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Current open orders
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/openOrders",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalSymbol": optionalSymbol,
                "recvWindow": recvWindow,
            },
        )

    def delete_api_open_orders(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Cancel all Open Orders on a Symbol (TRADE)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Cancelled orders
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="DELETE",
            path="/api/v3/openOrders",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_api_all_orders(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        orderId: int = None,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        All Orders (USER_DATA)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: Order id
            Type: int
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param limit: Default 500; max 1000.
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Current open orders
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/allOrders",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def post_api_order_list_oco(
        self,
        symbol: str,
        side: str,
        quantity: float,
        aboveType: str,
        belowType: str,
        timestamp: int,
        signature: str,
        listClientOrderId: str = None,
        aboveClientOrderId: str = None,
        aboveIcebergQty: float = None,
        abovePrice: float = None,
        aboveStopPrice: float = None,
        aboveTrailingDelta: float = None,
        aboveTimeInForce: str = None,
        aboveStrategyId: float = None,
        aboveStrategyType: int = None,
        belowClientOrderId: str = None,
        belowIcebergQty: float = None,
        belowPrice: float = None,
        belowStopPrice: float = None,
        belowTrailingDelta: float = None,
        belowTimeInForce: str = None,
        belowStrategyId: float = None,
        belowStrategyType: int = None,
        newOrderRespType: str = None,
        selfTradePreventionMode: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                New Order list - OCO (TRADE)
                Parameters:
                :param symbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param side:
                    Type: str
                :param quantity:
                    Type: float
                :param aboveType: Supported values : `STOP_LOSS_LIMIT`, `STOP_LOSS`, `LIMIT_MAKER`
                    Type:str
                :param belowType: Supported values : `STOP_LOSS_LIMIT`, `STOP_LOSS`, `LIMIT_MAKER`
                    Type:str
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param listClientOrderId: Arbitrary unique ID among open order lists. Automatically generated if not sent.
        A new order list with the same `listClientOrderId` is accepted only when the previous one is filled or completely expired.
        `listClientOrderId` is distinct from the `aboveClientOrderId` and the `belowCLientOrderId`.
                    Type:str
                :param aboveClientOrderId: Arbitrary unique ID among open orders for the above order. Automatically generated if not sent
                    Type:str
                :param aboveIcebergQty: Note that this can only be used if `aboveTimeInForce` is `GTC`.
                    Type:float
                :param abovePrice: No description.
                    Type:float
                :param aboveStopPrice: Can be used if `aboveType` is `STOP_LOSS` or `STOP_LOSS_LIMIT`.
        Either `aboveStopPrice` or `aboveTrailingDelta` or both, must be specified.
                    Type:float
                :param aboveTrailingDelta: No description.
                    Type:float
                :param aboveTimeInForce: Required if the `aboveType` is `STOP_LOSS_LIMIT`.
                    Type:str
                :param aboveStrategyId: Arbitrary numeric value identifying the above order within an order strategy.
                    Type:float
                :param aboveStrategyType: Arbitrary numeric value identifying the above order strategy.
        Values smaller than 1000000 are reserved and cannot be used.
                    Type:int
                :param belowClientOrderId: Arbitrary unique ID among open orders for the below order. Automatically generated if not sent
                    Type:str
                :param belowIcebergQty: Note that this can only be used if `belowTimeInForce` is `GTC`.
                    Type:float
                :param belowPrice: Can be used if `belowType` is `STOP_LOSS_LIMIT` or `LIMIT_MAKER` to specify the limit price.
                    Type:float
                :param belowStopPrice: Can be used if `belowType` is `STOP_LOSS` or `STOP_LOSS_LIMIT`.
        Either `belowStopPrice` or `belowTrailingDelta` or both, must be specified.
                    Type:float
                :param belowTrailingDelta: No description.
                    Type:float
                :param belowTimeInForce: Required if the `belowType` is `STOP_LOSS_LIMIT`.
                    Type:str
                :param belowStrategyId: Arbitrary numeric value identifying the below order within an order strategy.
                    Type:float
                :param belowStrategyType: Arbitrary numeric value identifying the below order strategy.
        Values smaller than 1000000 are reserved and cannot be used.
                    Type:int
                :param newOrderRespType: Set the response JSON. MARKET and LIMIT order types default to FULL, all other orders default to ACK.
                    Type: str
                :param selfTradePreventionMode: The allowed enums is dependent on what is configured on the symbol. The possible supported values are EXPIRE_TAKER, EXPIRE_MAKER, EXPIRE_BOTH, NONE.
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: New OCO details
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/api/v3/orderList/oco",
            params={
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "aboveType": aboveType,
                "belowType": belowType,
                "timestamp": timestamp,
                "signature": signature,
                "listClientOrderId": listClientOrderId,
                "aboveClientOrderId": aboveClientOrderId,
                "aboveIcebergQty": aboveIcebergQty,
                "abovePrice": abovePrice,
                "aboveStopPrice": aboveStopPrice,
                "aboveTrailingDelta": aboveTrailingDelta,
                "aboveTimeInForce": aboveTimeInForce,
                "aboveStrategyId": aboveStrategyId,
                "aboveStrategyType": aboveStrategyType,
                "belowClientOrderId": belowClientOrderId,
                "belowIcebergQty": belowIcebergQty,
                "belowPrice": belowPrice,
                "belowStopPrice": belowStopPrice,
                "belowTrailingDelta": belowTrailingDelta,
                "belowTimeInForce": belowTimeInForce,
                "belowStrategyId": belowStrategyId,
                "belowStrategyType": belowStrategyType,
                "newOrderRespType": newOrderRespType,
                "selfTradePreventionMode": selfTradePreventionMode,
                "recvWindow": recvWindow,
            },
        )

    def post_api_order_list_oto(
        self,
        symbol: str,
        workingType: str,
        workingSide: str,
        workingPrice: float,
        workingQuantity: float,
        workingIcebergQty: float,
        pendingType: str,
        pendingSide: str,
        pendingQuantity: float,
        timestamp: int,
        signature: str,
        listClientOrderId: str = None,
        ocoNewOrderRespType: str = None,
        selfTradePreventionMode: str = None,
        workingClientOrderId: str = None,
        workingTimeInForce: str = None,
        workingStrategyId: float = None,
        workingStrategyType: int = None,
        pendingClientOrderId: str = None,
        pendingPrice: float = None,
        pendingStopPrice: float = None,
        pendingTrailingDelta: float = None,
        pendingIcebergQty: float = None,
        pendingTimeInForce: str = None,
        pendingStrategyId: float = None,
        pendingStrategyType: int = None,
    ) -> Dict[str, Any]:
        """
                New Order List - OTO (TRADE)
                Parameters:
                :param symbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param workingType: Supported values: LIMIT,LIMIT_MAKER
                    Type: str
                :param workingSide: BUY,SELL
                    Type: str
                :param workingPrice:
                    Type: float
                :param workingQuantity: Sets the quantity for the working order.
                    Type: float
                :param workingIcebergQty: This can only be used if workingTimeInForce is GTC.
                    Type: float
                :param pendingType: Supported values: Order Types Note that MARKET orders using quoteOrderQty are not supported.
                    Type: str
                :param pendingSide: BUY,SELL
                    Type: str
                :param pendingQuantity: Sets the quantity for the pending order.
                    Type: float
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param listClientOrderId: Arbitrary unique ID among open order lists. Automatically generated if not sent.
        A new order list with the same `listClientOrderId` is accepted only when the previous one is filled or completely expired.
        `listClientOrderId` is distinct from the `workingClientOrderId` and the `pendingClientOrderId`.
                    Type:str
                :param ocoNewOrderRespType: Set the response JSON.
                    Type: str
                :param selfTradePreventionMode: The allowed enums is dependent on what is configured on the symbol. The possible supported values are EXPIRE_TAKER, EXPIRE_MAKER, EXPIRE_BOTH, NONE.
                    Type: str
                :param workingClientOrderId: Arbitrary unique ID among open orders for the working order. Automatically generated if not sent.
                    Type: str
                :param workingTimeInForce: GTC, IOC, FOK
                    Type: str
                :param workingStrategyId: Arbitrary numeric value identifying the working order within an order strategy.
                    Type:float
                :param workingStrategyType: Arbitrary numeric value identifying the working order strategy.
        Values smaller than 1000000 are reserved and cannot be used.
                    Type:int
                :param pendingClientOrderId: Arbitrary unique ID among open orders for the pending order. Automatically generated if not sent.
                    Type: str
                :param pendingPrice:
                    Type: float
                :param pendingStopPrice:
                    Type: float
                :param pendingTrailingDelta:
                    Type: float
                :param pendingIcebergQty: This can only be used if pendingTimeInForce is GTC.
                    Type: float
                :param pendingTimeInForce: GTC, IOC, FOK
                    Type: str
                :param pendingStrategyId: Arbitrary numeric value identifying the pending order within an order strategy.
                    Type:float
                :param pendingStrategyType: Arbitrary numeric value identifying the pending order strategy.
        Values smaller than 1000000 are reserved and cannot be used.
                    Type:int.
                :returns: New OTO details
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/api/v3/orderList/oto",
            params={
                "symbol": symbol,
                "workingType": workingType,
                "workingSide": workingSide,
                "workingPrice": workingPrice,
                "workingQuantity": workingQuantity,
                "workingIcebergQty": workingIcebergQty,
                "pendingType": pendingType,
                "pendingSide": pendingSide,
                "pendingQuantity": pendingQuantity,
                "timestamp": timestamp,
                "signature": signature,
                "listClientOrderId": listClientOrderId,
                "ocoNewOrderRespType": ocoNewOrderRespType,
                "selfTradePreventionMode": selfTradePreventionMode,
                "workingClientOrderId": workingClientOrderId,
                "workingTimeInForce": workingTimeInForce,
                "workingStrategyId": workingStrategyId,
                "workingStrategyType": workingStrategyType,
                "pendingClientOrderId": pendingClientOrderId,
                "pendingPrice": pendingPrice,
                "pendingStopPrice": pendingStopPrice,
                "pendingTrailingDelta": pendingTrailingDelta,
                "pendingIcebergQty": pendingIcebergQty,
                "pendingTimeInForce": pendingTimeInForce,
                "pendingStrategyId": pendingStrategyId,
                "pendingStrategyType": pendingStrategyType,
            },
        )

    def post_api_order_list_otoco(
        self,
        symbol: str,
        workingType: str,
        workingSide: str,
        workingPrice: float,
        workingQuantity: float,
        workingIcebergQty: float,
        pendingSide: str,
        pendingQuantity: float,
        pendingAboveType: str,
        timestamp: int,
        signature: str,
        listClientOrderId: str = None,
        ocoNewOrderRespType: str = None,
        selfTradePreventionMode: str = None,
        workingClientOrderId: str = None,
        workingTimeInForce: str = None,
        workingStrategyId: float = None,
        workingStrategyType: int = None,
        pendingAboveClientOrderId: str = None,
        pendingAbovePrice: float = None,
        pendingAboveStopPrice: float = None,
        pendingAboveTrailingDelta: float = None,
        pendingAboveIcebergQty: float = None,
        pendingAboveTimeInForce: str = None,
        pendingAboveStrategyId: float = None,
        pendingAboveStrategyType: int = None,
        pendingBelowType: str = None,
        pendingBelowClientOrderId: str = None,
        pendingBelowPrice: float = None,
        pendingBelowStopPrice: float = None,
        pendingBelowTrailingDelta: float = None,
        pendingBelowIcebergQty: float = None,
        pendingBelowTimeInForce: str = None,
        pendingBelowStrategyId: float = None,
        pendingBelowStrategyType: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                New Order List - OTOCO (TRADE)
                Parameters:
                :param symbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param workingType: Supported values: LIMIT,LIMIT_MAKER
                    Type: str
                :param workingSide: BUY,SELL
                    Type: str
                :param workingPrice:
                    Type: float
                :param workingQuantity: Sets the quantity for the working order.
                    Type: float
                :param workingIcebergQty: This can only be used if workingTimeInForce is GTC.
                    Type: float
                :param pendingSide: BUY,SELL
                    Type: str
                :param pendingQuantity: Sets the quantity for the pending order.
                    Type: float
                :param pendingAboveType: Supported values: LIMIT_MAKER, STOP_LOSS, and STOP_LOSS_LIMIT
                    Type: str
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param listClientOrderId: Arbitrary unique ID among open order lists. Automatically generated if not sent.
        A new order list with the same `listClientOrderId` is accepted only when the previous one is filled or completely expired.
        `listClientOrderId` is distinct from the `workingClientOrderId` and the `pendingClientOrderId`.
                    Type:str
                :param ocoNewOrderRespType: Set the response JSON.
                    Type: str
                :param selfTradePreventionMode: The allowed enums is dependent on what is configured on the symbol. The possible supported values are EXPIRE_TAKER, EXPIRE_MAKER, EXPIRE_BOTH, NONE.
                    Type: str
                :param workingClientOrderId: Arbitrary unique ID among open orders for the working order. Automatically generated if not sent.
                    Type: str
                :param workingTimeInForce: GTC, IOC, FOK
                    Type: str
                :param workingStrategyId: Arbitrary numeric value identifying the working order within an order strategy.
                    Type:float
                :param workingStrategyType: Arbitrary numeric value identifying the working order strategy.
        Values smaller than 1000000 are reserved and cannot be used.
                    Type:int
                :param pendingAboveClientOrderId: Arbitrary unique ID among open orders for the pending above order. Automatically generated if not sent.
                    Type: str
                :param pendingAbovePrice:
                    Type: float
                :param pendingAboveStopPrice:
                    Type: float
                :param pendingAboveTrailingDelta:
                    Type: float
                :param pendingAboveIcebergQty: This can only be used if pendingAboveTimeInForce is GTC.
                    Type: float
                :param pendingAboveTimeInForce:
                    Type: str
                :param pendingAboveStrategyId: Arbitrary numeric value identifying the pending above order within an order strategy.
                    Type:float
                :param pendingAboveStrategyType: Arbitrary numeric value identifying the pending above order strategy.
        Values smaller than 1000000 are reserved and cannot be used.
                    Type:int
                :param pendingBelowType: Supported values: LIMIT_MAKER, STOP_LOSS, and STOP_LOSS_LIMIT
                    Type: str
                :param pendingBelowClientOrderId: Arbitrary unique ID among open orders for the pending below order. Automatically generated if not sent.
                    Type: str
                :param pendingBelowPrice:
                    Type: float
                :param pendingBelowStopPrice:
                    Type: float
                :param pendingBelowTrailingDelta:
                    Type: float
                :param pendingBelowIcebergQty: This can only be used if pendingBelowTimeInForce is GTC.
                    Type: float
                :param pendingBelowTimeInForce:
                    Type: str
                :param pendingBelowStrategyId: Arbitrary numeric value identifying the pending below order within an order strategy.
                    Type:float
                :param pendingBelowStrategyType: Arbitrary numeric value identifying the pending below order strategy.
        Values smaller than 1000000 are reserved and cannot be used.
                    Type:int
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: New OTOCO details
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/api/v3/orderList/otoco",
            params={
                "symbol": symbol,
                "workingType": workingType,
                "workingSide": workingSide,
                "workingPrice": workingPrice,
                "workingQuantity": workingQuantity,
                "workingIcebergQty": workingIcebergQty,
                "pendingSide": pendingSide,
                "pendingQuantity": pendingQuantity,
                "pendingAboveType": pendingAboveType,
                "timestamp": timestamp,
                "signature": signature,
                "listClientOrderId": listClientOrderId,
                "ocoNewOrderRespType": ocoNewOrderRespType,
                "selfTradePreventionMode": selfTradePreventionMode,
                "workingClientOrderId": workingClientOrderId,
                "workingTimeInForce": workingTimeInForce,
                "workingStrategyId": workingStrategyId,
                "workingStrategyType": workingStrategyType,
                "pendingAboveClientOrderId": pendingAboveClientOrderId,
                "pendingAbovePrice": pendingAbovePrice,
                "pendingAboveStopPrice": pendingAboveStopPrice,
                "pendingAboveTrailingDelta": pendingAboveTrailingDelta,
                "pendingAboveIcebergQty": pendingAboveIcebergQty,
                "pendingAboveTimeInForce": pendingAboveTimeInForce,
                "pendingAboveStrategyId": pendingAboveStrategyId,
                "pendingAboveStrategyType": pendingAboveStrategyType,
                "pendingBelowType": pendingBelowType,
                "pendingBelowClientOrderId": pendingBelowClientOrderId,
                "pendingBelowPrice": pendingBelowPrice,
                "pendingBelowStopPrice": pendingBelowStopPrice,
                "pendingBelowTrailingDelta": pendingBelowTrailingDelta,
                "pendingBelowIcebergQty": pendingBelowIcebergQty,
                "pendingBelowTimeInForce": pendingBelowTimeInForce,
                "pendingBelowStrategyId": pendingBelowStrategyId,
                "pendingBelowStrategyType": pendingBelowStrategyType,
                "recvWindow": recvWindow,
            },
        )

    def get_api_order_list(
        self,
        timestamp: int,
        signature: str,
        orderListId: int = None,
        origClientOrderId: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query OCO (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderListId: Order list id
            Type: int
        :param origClientOrderId: Order id from client
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: OCO details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/orderList",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "orderListId": orderListId,
                "origClientOrderId": origClientOrderId,
                "recvWindow": recvWindow,
            },
        )

    def delete_api_order_list(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        orderListId: int = None,
        listClientOrderId: str = None,
        newClientOrderId: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Cancel OCO (TRADE)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderListId: Order list id
            Type: int
        :param listClientOrderId: A unique Id for the entire orderList
            Type: str
        :param newClientOrderId: Used to uniquely identify this cancel. Automatically generated by default
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Report on deleted OCO
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="DELETE",
            path="/api/v3/orderList",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "orderListId": orderListId,
                "listClientOrderId": listClientOrderId,
                "newClientOrderId": newClientOrderId,
                "recvWindow": recvWindow,
            },
        )

    def get_api_all_order_list(
        self,
        timestamp: int,
        signature: str,
        fromId: int = None,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query all OCO (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param fromId: Trade id to fetch from. Default gets most recent trades.
            Type: int
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param limit: Default 500; max 1000.
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of OCO orders
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/allOrderList",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "fromId": fromId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_api_open_order_list(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Open OCO (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of OCO orders
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/openOrderList",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_api_sor_order(
        self,
        symbol: str,
        side: str,
        orderType: str,
        quantity: float,
        timestamp: int,
        signature: str,
        timeInForce: str = None,
        price: float = None,
        newClientOrderId: str = None,
        strategyId: int = None,
        strategyType: int = None,
        icebergQty: float = None,
        newOrderRespType: str = None,
        selfTradePreventionMode: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        New order using SOR (TRADE)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param side:
            Type: str
        :param orderType: Order type
            Type: str
        :param quantity:
            Type: float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param timeInForce: Order time in force
            Type: str
        :param price: No description.
            Type:float
        :param newClientOrderId: Used to uniquely identify this cancel. Automatically generated by default
            Type: str
        :param strategyId:
            Type: int
        :param strategyType: The value cannot be less than 1000000.
            Type: int
        :param icebergQty: Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
            Type: float
        :param newOrderRespType: Set the response JSON. MARKET and LIMIT order types default to FULL, all other orders default to ACK.
            Type: str
        :param selfTradePreventionMode: The allowed enums is dependent on what is configured on the symbol. The possible supported values are EXPIRE_TAKER, EXPIRE_MAKER, EXPIRE_BOTH, NONE.
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: New order details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/api/v3/sor/order",
            params={
                "symbol": symbol,
                "side": side,
                "orderType": orderType,
                "quantity": quantity,
                "timestamp": timestamp,
                "signature": signature,
                "timeInForce": timeInForce,
                "price": price,
                "newClientOrderId": newClientOrderId,
                "strategyId": strategyId,
                "strategyType": strategyType,
                "icebergQty": icebergQty,
                "newOrderRespType": newOrderRespType,
                "selfTradePreventionMode": selfTradePreventionMode,
                "recvWindow": recvWindow,
            },
        )

    def post_api_sor_order_test(
        self,
        symbol: str,
        side: str,
        orderType: str,
        quantity: float,
        timestamp: int,
        signature: str,
        timeInForce: str = None,
        price: float = None,
        newClientOrderId: str = None,
        strategyId: int = None,
        strategyType: int = None,
        icebergQty: float = None,
        newOrderRespType: str = None,
        selfTradePreventionMode: str = None,
        computeCommissionRates: bool = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Test new order using SOR (TRADE)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param side:
            Type: str
        :param orderType: Order type
            Type: str
        :param quantity:
            Type: float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param timeInForce: Order time in force
            Type: str
        :param price: No description.
            Type:float
        :param newClientOrderId: Used to uniquely identify this cancel. Automatically generated by default
            Type: str
        :param strategyId:
            Type: int
        :param strategyType: The value cannot be less than 1000000.
            Type: int
        :param icebergQty: Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
            Type: float
        :param newOrderRespType: Set the response JSON. MARKET and LIMIT order types default to FULL, all other orders default to ACK.
            Type: str
        :param selfTradePreventionMode: The allowed enums is dependent on what is configured on the symbol. The possible supported values are EXPIRE_TAKER, EXPIRE_MAKER, EXPIRE_BOTH, NONE.
            Type: str
        :param computeCommissionRates: Default: false
            Type:bool
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Test new order
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/api/v3/sor/order/test",
            params={
                "symbol": symbol,
                "side": side,
                "orderType": orderType,
                "quantity": quantity,
                "timestamp": timestamp,
                "signature": signature,
                "timeInForce": timeInForce,
                "price": price,
                "newClientOrderId": newClientOrderId,
                "strategyId": strategyId,
                "strategyType": strategyType,
                "icebergQty": icebergQty,
                "newOrderRespType": newOrderRespType,
                "selfTradePreventionMode": selfTradePreventionMode,
                "computeCommissionRates": computeCommissionRates,
                "recvWindow": recvWindow,
            },
        )

    def get_api_account(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Account Information (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Account details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/account",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_api_my_trades(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        orderId: int = None,
        startTime: int = None,
        endTime: int = None,
        fromId: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Account Trade List (USER_DATA)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: This can only be used in combination with symbol.
            Type:int
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param fromId: Trade id to fetch from. Default gets most recent trades.
            Type: int
        :param limit: Default 500; max 1000.
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of trades
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/myTrades",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "startTime": startTime,
                "endTime": endTime,
                "fromId": fromId,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_api_rate_limit_order(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Current Order Count Usage (TRADE)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Order rate limits
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/rateLimit/order",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_api_my_prevented_matches(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        preventedMatchId: int = None,
        orderId: int = None,
        fromPreventedMatchId: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Prevented Matches
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param preventedMatchId:
            Type: int
        :param orderId: Order id
            Type: int
        :param fromPreventedMatchId: No description.
            Type:int
        :param limit: Default 500; max 1000.
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Order list that were expired due to STP
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/myPreventedMatches",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "preventedMatchId": preventedMatchId,
                "orderId": orderId,
                "fromPreventedMatchId": fromPreventedMatchId,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_api_my_allocations(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        fromAllocationId: int = None,
        limit: int = None,
        orderId: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Allocations (USER_DATA)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param fromAllocationId: No description.
            Type:int
        :param limit: Default 500; max 1000.
            Type: int
        :param orderId: Order id
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Allocations resulting from SOR order placement
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/myAllocations",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "fromAllocationId": fromAllocationId,
                "limit": limit,
                "orderId": orderId,
                "recvWindow": recvWindow,
            },
        )

    def get_api_account_commission(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
    ) -> Dict[str, Any]:
        """
        Query Commission Rates (USER_DATA)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str.
        :returns: Current account commission rates.
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/api/v3/account/commission",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
            },
        )

    def post_sapi_margin_borrow_repay(
        self,
        asset: str,
        isIsolated: str,
        symbol: str,
        amount: float,
        type_: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Margin account borrow/repay(MARGIN)
        Parameters:
        :param asset:
            Type: str
        :param isIsolated: TRUE for isolated margin, FALSE for crossed margin
            Type:str
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param amount:
            Type: float
        :param type_: BORROW or REPAY
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Margin account borrow/repay
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/margin/borrow-repay",
            params={
                "asset": asset,
                "isIsolated": isIsolated,
                "symbol": symbol,
                "amount": amount,
                "type": type_,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_borrow_repay(
        self,
        asset: str,
        type_: str,
        timestamp: int,
        signature: str,
        isolatedSymbol: str = None,
        txId: int = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query borrow/repay records in Margin account(USER_DATA)
        Parameters:
        :param asset:
            Type: str
        :param type_: BORROW or REPAY
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param isolatedSymbol: Isolated symbol
            Type: str
        :param txId: tranId in POST /sapi/v1/margin/loan
            Type:int
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Margin account borrow/repay
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/borrow-repay",
            params={
                "asset": asset,
                "type": type_,
                "timestamp": timestamp,
                "signature": signature,
                "isolatedSymbol": isolatedSymbol,
                "txId": txId,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_transfer(
        self,
        timestamp: int,
        signature: str,
        optionalAsset: str = None,
        getCrossMargingTransferHistoryType: str = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        isolatedSymbol: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Cross Margin Transfer History (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalAsset:
            Type: str
        :param getCrossMargingTransferHistoryType:
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param isolatedSymbol: Isolated symbol
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Margin account transfer history, response in descending order
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/transfer",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalAsset": optionalAsset,
                "getCrossMargingTransferHistoryType": getCrossMargingTransferHistoryType,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "isolatedSymbol": isolatedSymbol,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_all_assets(
        self,
        asset: str,
    ) -> Dict[str, Any]:
        """
        Get All Margin Assets (MARKET_DATA)
        Parameters:
        :param asset:
            Type: str.
        :returns: Assets details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/allAssets",
            params={
                "asset": asset,
            },
        )

    def get_sapi_margin_all_pairs(
        self,
        symbol: str,
    ) -> Dict[str, Any]:
        """
        Get All Cross Margin Pairs (MARKET_DATA)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str.
        :returns: Margin pairs
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/allPairs",
            params={
                "symbol": symbol,
            },
        )

    def get_sapi_margin_price_index(
        self,
        symbol: str,
    ) -> Dict[str, Any]:
        """
        Query Margin PriceIndex (MARKET_DATA)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str.
        :returns: Price index
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/priceIndex",
            params={
                "symbol": symbol,
            },
        )

    def get_sapi_margin_order(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        isIsolatedMargin: str = None,
        orderId: int = None,
        origClientOrderId: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Query Margin Account's Order (USER_DATA)
                Parameters:
                :param symbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param isIsolatedMargin: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param orderId: Order id
                    Type: int
                :param origClientOrderId: Order id from client
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Interest History, response in descending order
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/order",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "isIsolatedMargin": isIsolatedMargin,
                "orderId": orderId,
                "origClientOrderId": origClientOrderId,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_margin_order(
        self,
        symbol: str,
        side: str,
        orderType: str,
        quantity: float,
        autoRepayAtCancel: bool,
        timestamp: int,
        signature: str,
        isIsolatedMargin: str = None,
        quoteOrderQty: float = None,
        optionalPrice: float = None,
        stopPrice: float = None,
        newClientOrderId: str = None,
        icebergQty: float = None,
        ocoNewOrderRespType: str = None,
        sideEffectType: str = None,
        timeInForce: str = None,
        selfTradePreventionMode: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Margin Account New Order (TRADE)
                Parameters:
                :param symbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param side:
                    Type: str
                :param orderType: Order type
                    Type: str
                :param quantity:
                    Type: float
                :param autoRepayAtCancel: No description.
                    Type:bool
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param isIsolatedMargin: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param quoteOrderQty: Quote quantity
                    Type: float
                :param optionalPrice: Order price
                    Type: float
                :param stopPrice: Used with STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, and TAKE_PROFIT_LIMIT orders.
                    Type: float
                :param newClientOrderId: Used to uniquely identify this cancel. Automatically generated by default
                    Type: str
                :param icebergQty: Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
                    Type: float
                :param ocoNewOrderRespType: Set the response JSON.
                    Type: str
                :param sideEffectType: Default `NO_SIDE_EFFECT`
                    Type: str
                :param timeInForce: Order time in force
                    Type: str
                :param selfTradePreventionMode: The allowed enums is dependent on what is configured on the symbol. The possible supported values are EXPIRE_TAKER, EXPIRE_MAKER, EXPIRE_BOTH, NONE.
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Margin order info
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/margin/order",
            params={
                "symbol": symbol,
                "side": side,
                "orderType": orderType,
                "quantity": quantity,
                "autoRepayAtCancel": autoRepayAtCancel,
                "timestamp": timestamp,
                "signature": signature,
                "isIsolatedMargin": isIsolatedMargin,
                "quoteOrderQty": quoteOrderQty,
                "optionalPrice": optionalPrice,
                "stopPrice": stopPrice,
                "newClientOrderId": newClientOrderId,
                "icebergQty": icebergQty,
                "ocoNewOrderRespType": ocoNewOrderRespType,
                "sideEffectType": sideEffectType,
                "timeInForce": timeInForce,
                "selfTradePreventionMode": selfTradePreventionMode,
                "recvWindow": recvWindow,
            },
        )

    def delete_sapi_margin_order(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        isIsolatedMargin: str = None,
        orderId: int = None,
        origClientOrderId: str = None,
        newClientOrderId: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Margin Account Cancel Order (TRADE)
                Parameters:
                :param symbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param isIsolatedMargin: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param orderId: Order id
                    Type: int
                :param origClientOrderId: Order id from client
                    Type: str
                :param newClientOrderId: Used to uniquely identify this cancel. Automatically generated by default
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Cancelled margin order details
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="DELETE",
            path="/sapi/v1/margin/order",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "isIsolatedMargin": isIsolatedMargin,
                "orderId": orderId,
                "origClientOrderId": origClientOrderId,
                "newClientOrderId": newClientOrderId,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_interest_history(
        self,
        timestamp: int,
        signature: str,
        optionalAsset: str = None,
        isolatedSymbol: str = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        archived: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Interest History (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalAsset:
            Type: str
        :param isolatedSymbol: Isolated symbol
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param archived: Default: false. Set to true for archived data from 6 months ago
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Interest History, response in descending order
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/interestHistory",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalAsset": optionalAsset,
                "isolatedSymbol": isolatedSymbol,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "archived": archived,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_force_liquidation_rec(
        self,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        isolatedSymbol: str = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Force Liquidation Record (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param isolatedSymbol: Isolated symbol
            Type: str
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Force Liquidation History, response in descending order
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/forceLiquidationRec",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "isolatedSymbol": isolatedSymbol,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_account(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Cross Margin Account Details (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Margin account details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/account",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_open_orders(
        self,
        timestamp: int,
        signature: str,
        optionalSymbol: str = None,
        isIsolatedMargin: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Query Margin Account's Open Orders (USER_DATA)
                Parameters:
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param optionalSymbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param isIsolatedMargin: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Margin open orders list
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/openOrders",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalSymbol": optionalSymbol,
                "isIsolatedMargin": isIsolatedMargin,
                "recvWindow": recvWindow,
            },
        )

    def delete_sapi_margin_open_orders(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        isIsolatedMargin: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Margin Account Cancel all Open Orders on a Symbol (TRADE)
                Parameters:
                :param symbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param isIsolatedMargin: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Cancelled margin orders
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="DELETE",
            path="/sapi/v1/margin/openOrders",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "isIsolatedMargin": isIsolatedMargin,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_all_orders(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        isIsolatedMargin: str = None,
        orderId: int = None,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Query Margin Account's All Orders (USER_DATA)
                Parameters:
                :param symbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param isIsolatedMargin: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param orderId: Order id
                    Type: int
                :param startTime: UTC timestamp in ms
                    Type: int
                :param endTime: UTC timestamp in ms
                    Type: int
                :param limit: Default 500; max 1000.
                    Type: int
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Margin order list
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/allOrders",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "isIsolatedMargin": isIsolatedMargin,
                "orderId": orderId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_margin_order_oco(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        ocoStopPrice: float,
        timestamp: int,
        signature: str,
        isIsolatedMargin: str = None,
        listClientOrderId: str = None,
        limitClientOrderId: str = None,
        limitIcebergQty: float = None,
        stopClientOrderId: str = None,
        stopLimitPrice: float = None,
        stopIcebergQty: float = None,
        stopLimitTimeInForce: str = None,
        ocoNewOrderRespType: str = None,
        sideEffectType: str = None,
        selfTradePreventionMode: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Margin Account New OCO (TRADE)
                Parameters:
                :param symbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param side:
                    Type: str
                :param quantity:
                    Type: float
                :param price: Order price
                    Type: float
                :param ocoStopPrice:
                    Type: float
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param isIsolatedMargin: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param listClientOrderId: A unique Id for the entire orderList
                    Type: str
                :param limitClientOrderId: A unique Id for the limit order
                    Type: str
                :param limitIcebergQty:
                    Type: float
                :param stopClientOrderId: A unique Id for the stop loss/stop loss limit leg
                    Type: str
                :param stopLimitPrice: If provided, stopLimitTimeInForce is required.
                    Type: float
                :param stopIcebergQty:
                    Type: float
                :param stopLimitTimeInForce:
                    Type: str
                :param ocoNewOrderRespType: Set the response JSON.
                    Type: str
                :param sideEffectType: Default `NO_SIDE_EFFECT`
                    Type: str
                :param selfTradePreventionMode: The allowed enums is dependent on what is configured on the symbol. The possible supported values are EXPIRE_TAKER, EXPIRE_MAKER, EXPIRE_BOTH, NONE.
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: New Margin OCO details
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/margin/order/oco",
            params={
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "price": price,
                "ocoStopPrice": ocoStopPrice,
                "timestamp": timestamp,
                "signature": signature,
                "isIsolatedMargin": isIsolatedMargin,
                "listClientOrderId": listClientOrderId,
                "limitClientOrderId": limitClientOrderId,
                "limitIcebergQty": limitIcebergQty,
                "stopClientOrderId": stopClientOrderId,
                "stopLimitPrice": stopLimitPrice,
                "stopIcebergQty": stopIcebergQty,
                "stopLimitTimeInForce": stopLimitTimeInForce,
                "ocoNewOrderRespType": ocoNewOrderRespType,
                "sideEffectType": sideEffectType,
                "selfTradePreventionMode": selfTradePreventionMode,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_order_list(
        self,
        timestamp: int,
        signature: str,
        isIsolatedMargin: str = None,
        symbol: str = None,
        orderListId: int = None,
        origClientOrderId: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Query Margin Account's OCO (USER_DATA)
                Parameters:
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param isIsolatedMargin: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param symbol: Mandatory for isolated margin, not supported for cross margin
                    Type:str
                :param orderListId: Order list id
                    Type: int
                :param origClientOrderId: Order id from client
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Margin OCO details
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/orderList",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "isIsolatedMargin": isIsolatedMargin,
                "symbol": symbol,
                "orderListId": orderListId,
                "origClientOrderId": origClientOrderId,
                "recvWindow": recvWindow,
            },
        )

    def delete_sapi_margin_order_list(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        isIsolatedMargin: str = None,
        orderListId: int = None,
        listClientOrderId: str = None,
        newClientOrderId: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Margin Account Cancel OCO (TRADE)
                Parameters:
                :param symbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param isIsolatedMargin: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param orderListId: Order list id
                    Type: int
                :param listClientOrderId: A unique Id for the entire orderList
                    Type: str
                :param newClientOrderId: Used to uniquely identify this cancel. Automatically generated by default
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Margin OCO details
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="DELETE",
            path="/sapi/v1/margin/orderList",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "isIsolatedMargin": isIsolatedMargin,
                "orderListId": orderListId,
                "listClientOrderId": listClientOrderId,
                "newClientOrderId": newClientOrderId,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_all_order_list(
        self,
        timestamp: int,
        signature: str,
        isIsolatedMargin: str = None,
        symbol: str = None,
        fromId: str = None,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Query Margin Account's all OCO (USER_DATA)
                Parameters:
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param isIsolatedMargin: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param symbol: Mandatory for isolated margin, not supported for cross margin
                    Type:str
                :param fromId: If supplied, neither `startTime` or `endTime` can be provided
                    Type:str
                :param startTime: UTC timestamp in ms
                    Type: int
                :param endTime: UTC timestamp in ms
                    Type: int
                :param limit: Default Value: 500; Max Value: 1000
                    Type:int
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: List of Margin OCO orders
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/allOrderList",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "isIsolatedMargin": isIsolatedMargin,
                "symbol": symbol,
                "fromId": fromId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_open_order_list(
        self,
        timestamp: int,
        signature: str,
        isIsolatedMargin: str = None,
        symbol: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Query Margin Account's Open OCO (USER_DATA)
                Parameters:
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param isIsolatedMargin: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param symbol: Mandatory for isolated margin, not supported for cross margin
                    Type:str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: List of Open Margin OCO orders
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/openOrderList",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "isIsolatedMargin": isIsolatedMargin,
                "symbol": symbol,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_my_trades(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        isIsolatedMargin: str = None,
        startTime: int = None,
        endTime: int = None,
        fromId: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Query Margin Account's Trade List (USER_DATA)
                Parameters:
                :param symbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param isIsolatedMargin: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param startTime: UTC timestamp in ms
                    Type: int
                :param endTime: UTC timestamp in ms
                    Type: int
                :param fromId: Trade id to fetch from. Default gets most recent trades.
                    Type: int
                :param limit: Default 500; max 1000.
                    Type: int
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: List of margin trades
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/myTrades",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "isIsolatedMargin": isIsolatedMargin,
                "startTime": startTime,
                "endTime": endTime,
                "fromId": fromId,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_max_borrowable(
        self,
        asset: str,
        timestamp: int,
        signature: str,
        isolatedSymbol: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Max Borrow (USER_DATA)
        Parameters:
        :param asset:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param isolatedSymbol: Isolated symbol
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Details on max borrow amount
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/maxBorrowable",
            params={
                "asset": asset,
                "timestamp": timestamp,
                "signature": signature,
                "isolatedSymbol": isolatedSymbol,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_max_transferable(
        self,
        asset: str,
        timestamp: int,
        signature: str,
        isolatedSymbol: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Max Transfer-Out Amount (USER_DATA)
        Parameters:
        :param asset:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param isolatedSymbol: Isolated symbol
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Details on max transferable amount
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/maxTransferable",
            params={
                "asset": asset,
                "timestamp": timestamp,
                "signature": signature,
                "isolatedSymbol": isolatedSymbol,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_trade_coeff(
        self,
        email: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Summary of Margin account (USER_DATA)
        Parameters:
        :param email: Email Address
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Summary of Margin Account
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/tradeCoeff",
            params={
                "email": email,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_isolated_account(
        self,
        timestamp: int,
        signature: str,
        symbols: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Isolated Margin Account Info (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param symbols: Max 5 symbols can be sent; separated by ','
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Isolated Margin Account Info when "symbols" is not sent
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/isolated/account",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "symbols": symbols,
                "recvWindow": recvWindow,
            },
        )

    def delete_sapi_margin_isolated_account(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Disable Isolated Margin Account (TRADE)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Isolated Margin Account status
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="DELETE",
            path="/sapi/v1/margin/isolated/account",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_margin_isolated_account(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Enable Isolated Margin Account (TRADE)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Isolated Margin Account status
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/margin/isolated/account",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_isolated_account_limit(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Enabled Isolated Margin Account Limit (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Number of enabled Isolated Margin Account and its limit
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/isolated/accountLimit",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_isolated_all_pairs(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get All Isolated Margin Symbol(USER_DATA)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: All Isolated Margin Symbols
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/isolated/allPairs",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_bnb_burn(
        self,
        timestamp: int,
        signature: str,
        spotBNBBurn: str = None,
        interestBNBBurn: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Toggle BNB Burn On Spot Trade And Margin Interest (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param spotBNBBurn: Determines whether to use BNB to pay for trading fees on SPOT
            Type:str
        :param interestBNBBurn: Determines whether to use BNB to pay for margin loan's interest
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Status on BNB to pay for trading fees
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/bnbBurn",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "spotBNBBurn": spotBNBBurn,
                "interestBNBBurn": interestBNBBurn,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_bnb_burn(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get BNB Burn Status(USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Status on BNB to pay for trading fees
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/bnbBurn",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_interest_rate_history(
        self,
        asset: str,
        timestamp: int,
        signature: str,
        vipLevel: int = None,
        startTime: int = None,
        endTime: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Margin Interest Rate History (USER_DATA)
        Parameters:
        :param asset:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param vipLevel: Defaults to user's vip level
            Type: int
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Margin Interest Rate History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/interestRateHistory",
            params={
                "asset": asset,
                "timestamp": timestamp,
                "signature": signature,
                "vipLevel": vipLevel,
                "startTime": startTime,
                "endTime": endTime,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_cross_margin_data(
        self,
        timestamp: int,
        signature: str,
        vipLevel: int = None,
        optionalCoin: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Cross Margin Fee Data (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param vipLevel: Defaults to user's vip level
            Type: int
        :param optionalCoin: Coin name
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Cross Margin Fee Data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/crossMarginData",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "vipLevel": vipLevel,
                "optionalCoin": optionalCoin,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_isolated_margin_data(
        self,
        timestamp: int,
        signature: str,
        vipLevel: int = None,
        optionalSymbol: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Isolated Margin Fee Data (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param vipLevel: Defaults to user's vip level
            Type: int
        :param optionalSymbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Isolated Margin Fee Data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/isolatedMarginData",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "vipLevel": vipLevel,
                "optionalSymbol": optionalSymbol,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_isolated_margin_tier(
        self,
        symbol: str,
        timestamp: int,
        signature: str,
        tier: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Isolated Margin Tier Data (USER_DATA)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param tier: All margin tier data will be returned if tier is omitted
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Isolated Margin Tier Data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/isolatedMarginTier",
            params={
                "symbol": symbol,
                "timestamp": timestamp,
                "signature": signature,
                "tier": tier,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_rate_limit_order(
        self,
        timestamp: int,
        signature: str,
        optionalIsIsolated: str = None,
        symbol: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Query Current Margin Order Count Usage (TRADE)
                Parameters:
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param optionalIsIsolated: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param symbol: isolated symbol, mandatory for isolated margin
                    Type:str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Usage.
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/rateLimit/order",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalIsIsolated": optionalIsIsolated,
                "symbol": symbol,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_cross_margin_collateral_ratio(
        self,
    ) -> Dict[str, Any]:
        """
        Cross margin collateral ratio (MARKET_DATA).
        :returns: Margin collateral ratio
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/crossMarginCollateralRatio",
        )

    def get_sapi_margin_exchange_small_liability(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Small Liability Exchange Coin List (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: coin list
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/exchange-small-liability",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_exchange_small_liability_history(
        self,
        timestamp: int,
        signature: str,
        current: int = None,
        size: int = None,
        startTime: int = None,
        endTime: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Small Liability Exchange History (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: coin list
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/exchange-small-liability-history",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "current": current,
                "size": size,
                "startTime": startTime,
                "endTime": endTime,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_next_hourly_interest_rate(
        self,
        timestamp: int,
        signature: str,
        assets: str = None,
        isIsolated: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get a future hourly interest rate (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param assets: List of assets, separated by commas, up to 20
            Type:str
        :param isIsolated: for isolated margin or not, "TRUE", "FALSE"
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: hourly interest
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/next-hourly-interest-rate",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "assets": assets,
                "isIsolated": isIsolated,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_capital_flow(
        self,
        timestamp: int,
        signature: str,
        optionalAsset: str = None,
        symbol: str = None,
        type_: str = None,
        startTime: int = None,
        endTime: int = None,
        fromId: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get cross or isolated margin capital flow(USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalAsset:
            Type: str
        :param symbol: Required when querying isolated data
            Type:str
        :param type_: No description.
            Type:str
        :param startTime: Only supports querying the data of the last 90 days
            Type:int
        :param endTime: UTC timestamp in ms
            Type: int
        :param fromId: If fromId is set, the data with id > fromId will be returned. Otherwise the latest data will be returned
            Type:int
        :param limit: The number of data items returned each time is limited. Default 500; Max 1000.
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Margin capital flow
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/capital-flow",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalAsset": optionalAsset,
                "symbol": symbol,
                "type": type_,
                "startTime": startTime,
                "endTime": endTime,
                "fromId": fromId,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_delist_schedule(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get tokens or symbols delist schedule for cross margin and isolated margin (MARKET_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: tokens or symbols delist schedule
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/delist-schedule",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_available_inventory(
        self,
        type_: str,
        timestamp: int,
        signature: str,
    ) -> Dict[str, Any]:
        """
        Query Margin Available Inventory (USER_DATA)
        Parameters:
        :param type_: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str.
        :returns: Margin available Inventory
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/available-inventory",
            params={
                "type": type_,
                "timestamp": timestamp,
                "signature": signature,
            },
        )

    def post_sapi_margin_manual_liquidation(
        self,
        type_: str,
        timestamp: int,
        signature: str,
        symbol: str = None,
    ) -> Dict[str, Any]:
        """
        Margin manual liquidation(MARGIN)
        Parameters:
        :param type_: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param symbol: No description.
            Type:str.
        :returns: Margin manual liquidation
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/margin/manual-liquidation",
            params={
                "type": type_,
                "timestamp": timestamp,
                "signature": signature,
                "symbol": symbol,
            },
        )

    def post_sapi_margin_order_oto(
        self,
        symbol: str,
        workingType: str,
        workingSide: str,
        workingPrice: float,
        workingQuantity: float,
        workingIcebergQty: float,
        pendingType: str,
        pendingSide: str,
        pendingQuantity: float,
        timestamp: int,
        signature: str,
        isIsolatedMargin: str = None,
        listClientOrderId: str = None,
        ocoNewOrderRespType: str = None,
        sideEffectType: str = None,
        selfTradePreventionMode: str = None,
        autoRepayAtCancel: bool = None,
        workingClientOrderId: str = None,
        workingTimeInForce: str = None,
        pendingClientOrderId: str = None,
        pendingPrice: float = None,
        pendingStopPrice: float = None,
        pendingTrailingDelta: float = None,
        pendingIcebergQty: float = None,
        pendingTimeInForce: str = None,
    ) -> Dict[str, Any]:
        """
                Margin Account New OTO (TRADE)
                Parameters:
                :param symbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param workingType: Supported values: LIMIT,LIMIT_MAKER
                    Type: str
                :param workingSide: BUY,SELL
                    Type: str
                :param workingPrice:
                    Type: float
                :param workingQuantity: Sets the quantity for the working order.
                    Type: float
                :param workingIcebergQty: This can only be used if workingTimeInForce is GTC.
                    Type: float
                :param pendingType: Supported values: Order Types Note that MARKET orders using quoteOrderQty are not supported.
                    Type: str
                :param pendingSide: BUY,SELL
                    Type: str
                :param pendingQuantity: Sets the quantity for the pending order.
                    Type: float
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param isIsolatedMargin: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param listClientOrderId: Arbitrary unique ID among open order lists. Automatically generated if not sent.
        A new order list with the same `listClientOrderId` is accepted only when the previous one is filled or completely expired.
        `listClientOrderId` is distinct from the `workingClientOrderId` and the `pendingClientOrderId`.
                    Type:str
                :param ocoNewOrderRespType: Set the response JSON.
                    Type: str
                :param sideEffectType: Default `NO_SIDE_EFFECT`
                    Type:str
                :param selfTradePreventionMode: The allowed enums is dependent on what is configured on the symbol. The possible supported values are EXPIRE_TAKER, EXPIRE_MAKER, EXPIRE_BOTH, NONE.
                    Type: str
                :param autoRepayAtCancel: Only when MARGIN_BUY order takes effect, true means that the debt generated by the order needs to be repay after the order is cancelled. The default is true
                    Type:bool
                :param workingClientOrderId: Arbitrary unique ID among open orders for the working order. Automatically generated if not sent.
                    Type: str
                :param workingTimeInForce: GTC, IOC, FOK
                    Type: str
                :param pendingClientOrderId: Arbitrary unique ID among open orders for the pending order. Automatically generated if not sent.
                    Type: str
                :param pendingPrice:
                    Type: float
                :param pendingStopPrice:
                    Type: float
                :param pendingTrailingDelta:
                    Type: float
                :param pendingIcebergQty: This can only be used if pendingTimeInForce is GTC.
                    Type: float
                :param pendingTimeInForce: GTC, IOC, FOK
                    Type: str.
                :returns: OTO order
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/margin/order/oto",
            params={
                "symbol": symbol,
                "workingType": workingType,
                "workingSide": workingSide,
                "workingPrice": workingPrice,
                "workingQuantity": workingQuantity,
                "workingIcebergQty": workingIcebergQty,
                "pendingType": pendingType,
                "pendingSide": pendingSide,
                "pendingQuantity": pendingQuantity,
                "timestamp": timestamp,
                "signature": signature,
                "isIsolatedMargin": isIsolatedMargin,
                "listClientOrderId": listClientOrderId,
                "ocoNewOrderRespType": ocoNewOrderRespType,
                "sideEffectType": sideEffectType,
                "selfTradePreventionMode": selfTradePreventionMode,
                "autoRepayAtCancel": autoRepayAtCancel,
                "workingClientOrderId": workingClientOrderId,
                "workingTimeInForce": workingTimeInForce,
                "pendingClientOrderId": pendingClientOrderId,
                "pendingPrice": pendingPrice,
                "pendingStopPrice": pendingStopPrice,
                "pendingTrailingDelta": pendingTrailingDelta,
                "pendingIcebergQty": pendingIcebergQty,
                "pendingTimeInForce": pendingTimeInForce,
            },
        )

    def post_sapi_margin_order_otoco(
        self,
        symbol: str,
        workingType: str,
        workingSide: str,
        workingPrice: float,
        workingQuantity: float,
        workingIcebergQty: float,
        pendingSide: str,
        pendingQuantity: float,
        pendingAboveType: str,
        timestamp: int,
        signature: str,
        isIsolatedMargin: str = None,
        sideEffectType: str = None,
        autoRepayAtCancel: bool = None,
        listClientOrderId: str = None,
        ocoNewOrderRespType: str = None,
        selfTradePreventionMode: str = None,
        workingClientOrderId: str = None,
        workingTimeInForce: str = None,
        pendingAboveClientOrderId: str = None,
        pendingAbovePrice: float = None,
        pendingAboveStopPrice: float = None,
        pendingAboveTrailingDelta: float = None,
        pendingAboveIcebergQty: float = None,
        pendingAboveTimeInForce: str = None,
        pendingBelowType: str = None,
        pendingBelowClientOrderId: str = None,
        pendingBelowPrice: float = None,
        pendingBelowStopPrice: float = None,
        pendingBelowTrailingDelta: float = None,
        pendingBelowIcebergQty: float = None,
        pendingBelowTimeInForce: str = None,
    ) -> Dict[str, Any]:
        """
                Margin Account New OTOCO (TRADE)
                Parameters:
                :param symbol: Trading symbol, e.g. BNBUSDT
                    Type: str
                :param workingType: Supported values: LIMIT,LIMIT_MAKER
                    Type: str
                :param workingSide: BUY,SELL
                    Type: str
                :param workingPrice:
                    Type: float
                :param workingQuantity: Sets the quantity for the working order.
                    Type: float
                :param workingIcebergQty: This can only be used if workingTimeInForce is GTC.
                    Type: float
                :param pendingSide: BUY,SELL
                    Type: str
                :param pendingQuantity: Sets the quantity for the pending order.
                    Type: float
                :param pendingAboveType: Supported values: LIMIT_MAKER, STOP_LOSS, and STOP_LOSS_LIMIT
                    Type: str
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param isIsolatedMargin: * `TRUE` - For isolated margin
        * `FALSE` - Default, not for isolated margin
                    Type: str
                :param sideEffectType: Default `NO_SIDE_EFFECT`
                    Type:str
                :param autoRepayAtCancel: Only when MARGIN_BUY order takes effect, true means that the debt generated by the order needs to be repay after the order is cancelled. The default is true
                    Type:bool
                :param listClientOrderId: Arbitrary unique ID among open order lists. Automatically generated if not sent.
        A new order list with the same `listClientOrderId` is accepted only when the previous one is filled or completely expired.
        `listClientOrderId` is distinct from the `workingClientOrderId` and the `pendingClientOrderId`.
                    Type:str
                :param ocoNewOrderRespType: Set the response JSON.
                    Type: str
                :param selfTradePreventionMode: The allowed enums is dependent on what is configured on the symbol. The possible supported values are EXPIRE_TAKER, EXPIRE_MAKER, EXPIRE_BOTH, NONE.
                    Type: str
                :param workingClientOrderId: Arbitrary unique ID among open orders for the working order. Automatically generated if not sent.
                    Type: str
                :param workingTimeInForce: GTC, IOC, FOK
                    Type: str
                :param pendingAboveClientOrderId: Arbitrary unique ID among open orders for the pending above order. Automatically generated if not sent.
                    Type: str
                :param pendingAbovePrice:
                    Type: float
                :param pendingAboveStopPrice:
                    Type: float
                :param pendingAboveTrailingDelta:
                    Type: float
                :param pendingAboveIcebergQty: This can only be used if pendingAboveTimeInForce is GTC.
                    Type: float
                :param pendingAboveTimeInForce:
                    Type: str
                :param pendingBelowType: Supported values: LIMIT_MAKER, STOP_LOSS, and STOP_LOSS_LIMIT
                    Type: str
                :param pendingBelowClientOrderId: Arbitrary unique ID among open orders for the pending below order. Automatically generated if not sent.
                    Type: str
                :param pendingBelowPrice:
                    Type: float
                :param pendingBelowStopPrice:
                    Type: float
                :param pendingBelowTrailingDelta:
                    Type: float
                :param pendingBelowIcebergQty: This can only be used if pendingBelowTimeInForce is GTC.
                    Type: float
                :param pendingBelowTimeInForce:
                    Type: str.
                :returns: OTOCO order
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/margin/order/otoco",
            params={
                "symbol": symbol,
                "workingType": workingType,
                "workingSide": workingSide,
                "workingPrice": workingPrice,
                "workingQuantity": workingQuantity,
                "workingIcebergQty": workingIcebergQty,
                "pendingSide": pendingSide,
                "pendingQuantity": pendingQuantity,
                "pendingAboveType": pendingAboveType,
                "timestamp": timestamp,
                "signature": signature,
                "isIsolatedMargin": isIsolatedMargin,
                "sideEffectType": sideEffectType,
                "autoRepayAtCancel": autoRepayAtCancel,
                "listClientOrderId": listClientOrderId,
                "ocoNewOrderRespType": ocoNewOrderRespType,
                "selfTradePreventionMode": selfTradePreventionMode,
                "workingClientOrderId": workingClientOrderId,
                "workingTimeInForce": workingTimeInForce,
                "pendingAboveClientOrderId": pendingAboveClientOrderId,
                "pendingAbovePrice": pendingAbovePrice,
                "pendingAboveStopPrice": pendingAboveStopPrice,
                "pendingAboveTrailingDelta": pendingAboveTrailingDelta,
                "pendingAboveIcebergQty": pendingAboveIcebergQty,
                "pendingAboveTimeInForce": pendingAboveTimeInForce,
                "pendingBelowType": pendingBelowType,
                "pendingBelowClientOrderId": pendingBelowClientOrderId,
                "pendingBelowPrice": pendingBelowPrice,
                "pendingBelowStopPrice": pendingBelowStopPrice,
                "pendingBelowTrailingDelta": pendingBelowTrailingDelta,
                "pendingBelowIcebergQty": pendingBelowIcebergQty,
                "pendingBelowTimeInForce": pendingBelowTimeInForce,
            },
        )

    def post_sapi_margin_max_leverage(
        self,
        maxLeverage: int,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Adjust cross margin max leverage (USER_DATA)
        Parameters:
        :param maxLeverage: Can only adjust 3 or 5
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Adjust result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/margin/max-leverage",
            params={
                "maxLeverage": maxLeverage,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_margin_leverage_bracket(
        self,
    ) -> Dict[str, Any]:
        """
        Query Liability Coin Leverage Bracket in Cross Margin Pro Mode (MARKET_DATA).
        :returns: Leverage info
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/margin/leverageBracket",
        )

    def get_sapi_system_status(
        self,
    ) -> Dict[str, Any]:
        """
        System Status (System).
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/system/status",
        )

    def get_sapi_capital_config_getall(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        All Coins' Information (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: All coins details information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/capital/config/getall",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_account_snapshot(
        self,
        type_: str,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Daily Account Snapshot (USER_DATA)
        Parameters:
        :param type_: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param limit: No description.
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Account Snapshot
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/accountSnapshot",
            params={
                "type": type_,
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_account_disable_fast_withdraw_switch(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Disable Fast Withdraw Switch (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/account/disableFastWithdrawSwitch",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_account_enable_fast_withdraw_switch(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Enable Fast Withdraw Switch (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/account/enableFastWithdrawSwitch",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_capital_withdraw_apply(
        self,
        coin: str,
        address: str,
        amount: float,
        timestamp: int,
        signature: str,
        withdrawOrderId: str = None,
        network: str = None,
        addressTag: str = None,
        transactionFeeFlag: bool = None,
        name: str = None,
        walletType: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Withdraw (USER_DATA)
                Parameters:
                :param coin: Coin name
                    Type: str
                :param address: No description.
                    Type:str
                :param amount:
                    Type: float
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param withdrawOrderId: Client id for withdraw
                    Type:str
                :param network:
                    Type: str
                :param addressTag: Secondary address identifier for coins like XRP,XMR etc.
                    Type:str
                :param transactionFeeFlag: When making internal transfer
        - `true` ->  returning the fee to the destination account;
        - `false` -> returning the fee back to the departure account.
                    Type:bool
                :param name: No description.
                    Type:str
                :param walletType: The wallet type for withdraw，0-Spot wallet, 1- Funding wallet. Default is Spot wallet
                    Type:int
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Transafer Id
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/capital/withdraw/apply",
            params={
                "coin": coin,
                "address": address,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "withdrawOrderId": withdrawOrderId,
                "network": network,
                "addressTag": addressTag,
                "transactionFeeFlag": transactionFeeFlag,
                "name": name,
                "walletType": walletType,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_capital_deposit_hisrec(
        self,
        timestamp: int,
        signature: str,
        optionalCoin: str = None,
        status: int = None,
        startTime: int = None,
        endTime: int = None,
        offset: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Deposit History(supporting network) (USER_DATA)
                Parameters:
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param optionalCoin: Coin name
                    Type: str
                :param status: * `0` - pending
        * `6` - credited but cannot withdraw
        * `1` - success
                    Type:int
                :param startTime: UTC timestamp in ms
                    Type: int
                :param endTime: UTC timestamp in ms
                    Type: int
                :param offset:
                    Type: int
                :param limit: Default 500; max 1000.
                    Type: int
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: List of deposits
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/capital/deposit/hisrec",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalCoin": optionalCoin,
                "status": status,
                "startTime": startTime,
                "endTime": endTime,
                "offset": offset,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_capital_withdraw_history(
        self,
        timestamp: int,
        signature: str,
        optionalCoin: str = None,
        withdrawOrderId: str = None,
        status: int = None,
        startTime: int = None,
        endTime: int = None,
        offset: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Withdraw History (supporting network) (USER_DATA)
                Parameters:
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param optionalCoin: Coin name
                    Type: str
                :param withdrawOrderId: No description.
                    Type:str
                :param status: * `0` - Email Sent
        * `1` - Cancelled
        * `2` - Awaiting Approval
        * `3` - Rejected
        * `4` - Processing
        * `5` - Failure
        * `6` - Completed
                    Type:int
                :param startTime: UTC timestamp in ms
                    Type: int
                :param endTime: UTC timestamp in ms
                    Type: int
                :param offset:
                    Type: int
                :param limit: Default 500; max 1000.
                    Type: int
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: List of withdraw history
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/capital/withdraw/history",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalCoin": optionalCoin,
                "withdrawOrderId": withdrawOrderId,
                "status": status,
                "startTime": startTime,
                "endTime": endTime,
                "offset": offset,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_capital_deposit_address(
        self,
        coin: str,
        timestamp: int,
        signature: str,
        network: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Deposit Address (supporting network) (USER_DATA)
        Parameters:
        :param coin: Coin name
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param network:
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Deposit address info
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/capital/deposit/address",
            params={
                "coin": coin,
                "timestamp": timestamp,
                "signature": signature,
                "network": network,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_account_status(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Account Status (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/account/status",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_account_api_trading_status(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Account API Trading Status (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Account API trading status
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/account/apiTradingStatus",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_asset_dribblet(
        self,
        timestamp: int,
        signature: str,
        accountType: str = None,
        startTime: int = None,
        endTime: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        DustLog(USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param accountType: SPOT or MARGIN, default SPOT
            Type:str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Dust log records
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/asset/dribblet",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "accountType": accountType,
                "startTime": startTime,
                "endTime": endTime,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_asset_dust_btc(
        self,
        timestamp: int,
        signature: str,
        accountType: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Assets That Can Be Converted Into BNB (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param accountType: SPOT or MARGIN, default SPOT
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Account assets available to be converted to BNB
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/asset/dust-btc",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "accountType": accountType,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_asset_dust(
        self,
        asset: List[Any],
        timestamp: int,
        signature: str,
        accountType: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Dust Transfer (USER_DATA)
        Parameters:
        :param asset: The asset being converted. For example, asset=BTC&asset=USDT
            Type:List[Any]
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param accountType: SPOT or MARGIN, default SPOT
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Dust log records
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/asset/dust",
            params={
                "asset": asset,
                "timestamp": timestamp,
                "signature": signature,
                "accountType": accountType,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_asset_asset_dividend(
        self,
        timestamp: int,
        signature: str,
        optionalAsset: str = None,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Asset Dividend Record (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalAsset:
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param limit: No description.
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Records of asset devidend
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/asset/assetDividend",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalAsset": optionalAsset,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_asset_asset_detail(
        self,
        timestamp: int,
        signature: str,
        optionalAsset: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Asset Detail (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalAsset:
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Asset detail
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/asset/assetDetail",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalAsset": optionalAsset,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_asset_trade_fee(
        self,
        timestamp: int,
        signature: str,
        optionalSymbol: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Trade Fee (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalSymbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Trade fee info per symbol
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/asset/tradeFee",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalSymbol": optionalSymbol,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_asset_transfer(
        self,
        univTransferType: str,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        fromSymbol: str = None,
        toSymbol: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query User Universal Transfer History (USER_DATA)
        Parameters:
        :param univTransferType: Universal transfer type
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param fromSymbol: Must be sent when type are ISOLATEDMARGIN_MARGIN and ISOLATEDMARGIN_ISOLATEDMARGIN
            Type: str
        :param toSymbol: Must be sent when type are MARGIN_ISOLATEDMARGIN and ISOLATEDMARGIN_ISOLATEDMARGIN
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Universal transfer history
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/asset/transfer",
            params={
                "univTransferType": univTransferType,
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "fromSymbol": fromSymbol,
                "toSymbol": toSymbol,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_asset_transfer(
        self,
        univTransferType: str,
        asset: str,
        amount: float,
        timestamp: int,
        signature: str,
        fromSymbol: str = None,
        toSymbol: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        User Universal Transfer (USER_DATA)
        Parameters:
        :param univTransferType: Universal transfer type
            Type: str
        :param asset:
            Type: str
        :param amount:
            Type: float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param fromSymbol: Must be sent when type are ISOLATEDMARGIN_MARGIN and ISOLATEDMARGIN_ISOLATEDMARGIN
            Type: str
        :param toSymbol: Must be sent when type are MARGIN_ISOLATEDMARGIN and ISOLATEDMARGIN_ISOLATEDMARGIN
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Transfer id
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/asset/transfer",
            params={
                "univTransferType": univTransferType,
                "asset": asset,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "fromSymbol": fromSymbol,
                "toSymbol": toSymbol,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_asset_get_funding_asset(
        self,
        timestamp: int,
        signature: str,
        optionalAsset: str = None,
        needBtcValuation: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Funding Wallet (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalAsset:
            Type: str
        :param needBtcValuation:
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Funding asset detail
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/asset/get-funding-asset",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalAsset": optionalAsset,
                "needBtcValuation": needBtcValuation,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_asset_get_user_asset(
        self,
        timestamp: int,
        signature: str,
        optionalAsset: str = None,
        needBtcValuation: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        User Asset (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalAsset:
            Type: str
        :param needBtcValuation:
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: User assets
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v3/asset/getUserAsset",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalAsset": optionalAsset,
                "needBtcValuation": needBtcValuation,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_asset_convert_transfer(
        self,
        clientTranId: str,
        asset: str,
        amount: float,
        targetAsset: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Convert Transfer (USER_DATA)
        Parameters:
        :param clientTranId: The unique flag, the min length is 20
            Type:str
        :param asset:
            Type: str
        :param amount:
            Type: float
        :param targetAsset: Target asset you want to convert
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Conversion Information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/asset/convert-transfer",
            params={
                "clientTranId": clientTranId,
                "asset": asset,
                "amount": amount,
                "targetAsset": targetAsset,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_asset_convert_transfer_query_by_page(
        self,
        startTime: int,
        endTime: int,
        timestamp: int,
        signature: str,
        tranId: int = None,
        asset: str = None,
        accountType: str = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Convert Transfer (USER_DATA)
        Parameters:
        :param startTime: UTC timestamp in ms
            Type:int
        :param endTime: UTC timestamp in ms
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param tranId: The transaction id
            Type:int
        :param asset: If it is blank, we will match deducted asset and target asset.
            Type:str
        :param accountType: MAIN: main account. CARD: funding account. If it is blank, we will query spot and card wallet, otherwise, we just query the corresponding wallet
            Type:str
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Query Convert Transfer
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/asset/convert-transfer/queryByPage",
            params={
                "startTime": startTime,
                "endTime": endTime,
                "timestamp": timestamp,
                "signature": signature,
                "tranId": tranId,
                "asset": asset,
                "accountType": accountType,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_asset_ledger_transfer_cloud_mining_query_by_page(
        self,
        startTime: int,
        endTime: int,
        timestamp: int,
        signature: str,
        tranId: int = None,
        clientTranId: str = None,
        asset: str = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Cloud-Mining payment and refund history (USER_DATA)
        Parameters:
        :param startTime: UTC timestamp in ms
            Type:int
        :param endTime: UTC timestamp in ms
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param tranId: The transaction id
            Type:int
        :param clientTranId: The unique flag
            Type:str
        :param asset: If it is blank, we will query all assets
            Type:str
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Cloud Mining Payment and Refund History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/asset/ledger-transfer/cloud-mining/queryByPage",
            params={
                "startTime": startTime,
                "endTime": endTime,
                "timestamp": timestamp,
                "signature": signature,
                "tranId": tranId,
                "clientTranId": clientTranId,
                "asset": asset,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_account_api_restrictions(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get API Key Permission (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: API Key permissions
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/account/apiRestrictions",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_capital_contract_convertible_coins(
        self,
    ) -> Dict[str, Any]:
        """
        Query auto-converting stable coins (USER_DATA).
        :returns: User's auto-conversion settings i
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/capital/contract/convertible-coins",
        )

    def post_sapi_capital_contract_convertible_coins(
        self,
        coin: str,
        enable: bool,
    ) -> Dict[str, Any]:
        """
        Switch on/off BUSD and stable coins conversion (USER_DATA) (USER_DATA)
        Parameters:
        :param coin: Must be USDC, USDP or TUSD
            Type:str
        :param enable: true: turn on the auto-conversion. false: turn off the auto-conversion
            Type:bool.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/capital/contract/convertible-coins",
            params={
                "coin": coin,
                "enable": enable,
            },
        )

    def post_sapi_sub_account_virtual_sub_account(
        self,
        subAccountString: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Create a Virtual Sub-account(For Master Account)
        Parameters:
        :param subAccountString: Please input a string. We will create a virtual email using that string for you to register
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Return the created virtual email
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/sub-account/virtualSubAccount",
            params={
                "subAccountString": subAccountString,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_list_(
        self,
        timestamp: int,
        signature: str,
        optionalSubAccountEmail: str = None,
        isFreeze: str = None,
        page: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Sub-account List (For Master Account)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalSubAccountEmail: Sub-account email
            Type: str
        :param isFreeze: No description.
            Type:str
        :param page: Default 1
            Type: int
        :param limit: Default 1; max 200
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of sub-accounts
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/sub-account/list",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalSubAccountEmail": optionalSubAccountEmail,
                "isFreeze": isFreeze,
                "page": page,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_sub_transfer_history(
        self,
        timestamp: int,
        signature: str,
        optionalSubAccountFromEmail: str = None,
        optionalSubAccountToEmail: str = None,
        startTime: int = None,
        endTime: int = None,
        page: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Sub-account Spot Asset Transfer History (For Master Account)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalSubAccountFromEmail: Sub-account email
            Type: str
        :param optionalSubAccountToEmail: Sub-account email
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param page: Default 1
            Type: int
        :param limit: Default 1
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Sub-account Spot Asset Transfer History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/sub-account/sub/transfer/history",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalSubAccountFromEmail": optionalSubAccountFromEmail,
                "optionalSubAccountToEmail": optionalSubAccountToEmail,
                "startTime": startTime,
                "endTime": endTime,
                "page": page,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_futures_internal_transfer(
        self,
        subAccountEmail: str,
        futuresType: int,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        page: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Sub-account Futures Asset Transfer History (For Master Account)
        Parameters:
        :param subAccountEmail: Sub-account email
            Type: str
        :param futuresType: 1:USDT-margined Futures, 2: Coin-margined Futures
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param page: Default 1
            Type: int
        :param limit: Default value: 50, Max value: 500
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Sub-account Futures Asset Transfer History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/sub-account/futures/internalTransfer",
            params={
                "subAccountEmail": subAccountEmail,
                "futuresType": futuresType,
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "page": page,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_sub_account_futures_internal_transfer(
        self,
        subAccountFromEmail: str,
        subAccountToEmail: str,
        futuresType: int,
        asset: str,
        amount: float,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Sub-account Futures Asset Transfer (For Master Account)
        Parameters:
        :param subAccountFromEmail: Sender email
            Type: str
        :param subAccountToEmail: Recipient email
            Type: str
        :param futuresType: 1:USDT-margined Futures,2: Coin-margined Futures
            Type:int
        :param asset:
            Type: str
        :param amount:
            Type: float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Futures Asset Transfer Info
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/sub-account/futures/internalTransfer",
            params={
                "subAccountFromEmail": subAccountFromEmail,
                "subAccountToEmail": subAccountToEmail,
                "futuresType": futuresType,
                "asset": asset,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_assets(
        self,
        subAccountEmail: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Sub-account Assets (For Master Account)
        Parameters:
        :param subAccountEmail: Sub-account email
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of assets balances
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v3/sub-account/assets",
            params={
                "subAccountEmail": subAccountEmail,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_spot_summary(
        self,
        timestamp: int,
        signature: str,
        optionalSubAccountEmail: str = None,
        page: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Sub-account Spot Assets Summary (For Master Account)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalSubAccountEmail: Sub-account email
            Type: str
        :param page: Default 1
            Type: int
        :param size: Default:10 Max:20
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Summary of Sub-account Spot Assets
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/sub-account/spotSummary",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalSubAccountEmail": optionalSubAccountEmail,
                "page": page,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_capital_deposit_sub_address(
        self,
        subAccountEmail: str,
        coin: str,
        timestamp: int,
        signature: str,
        network: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Sub-account Spot Assets Summary (For Master Account)
        Parameters:
        :param subAccountEmail: Sub-account email
            Type: str
        :param coin: Coin name
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param network:
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Deposit address info
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/capital/deposit/subAddress",
            params={
                "subAccountEmail": subAccountEmail,
                "coin": coin,
                "timestamp": timestamp,
                "signature": signature,
                "network": network,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_capital_deposit_sub_hisrec(
        self,
        subAccountEmail: str,
        timestamp: int,
        signature: str,
        optionalCoin: str = None,
        status: int = None,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
        offset: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Sub-account Deposit History (For Master Account)
        Parameters:
        :param subAccountEmail: Sub-account email
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalCoin: Coin name
            Type: str
        :param status: 0(0:pending,6: credited but cannot withdraw, 1:success)
            Type:int
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param limit: No description.
            Type:int
        :param offset:
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Sub-account deposit history
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/capital/deposit/subHisrec",
            params={
                "subAccountEmail": subAccountEmail,
                "timestamp": timestamp,
                "signature": signature,
                "optionalCoin": optionalCoin,
                "status": status,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "offset": offset,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_capital_deposit_credit_apply(
        self,
        timestamp: int,
        signature: str,
        depositId: int = None,
        txId: str = None,
        subAccountId: int = None,
        subUserId: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        One click arrival deposit apply (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param depositId: Deposit record Id, priority use
            Type:int
        :param txId: Deposit txId, used when depositId is not specified
            Type:str
        :param subAccountId: No description.
            Type:int
        :param subUserId: No description.
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: deposit result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/capital/deposit/credit-apply",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "depositId": depositId,
                "txId": txId,
                "subAccountId": subAccountId,
                "subUserId": subUserId,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_asset_wallet_balance(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query User Wallet Balance (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: wallet balance
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/asset/wallet/balance",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_asset_custody_transfer_history(
        self,
        email: str,
        startTime: int,
        endTime: int,
        asset: str,
        timestamp: int,
        signature: str,
        type_: str = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query User Delegation History(For Master Account) (USER_DATA)
        Parameters:
        :param email: No description.
            Type:str
        :param startTime: No description.
            Type:int
        :param endTime: No description.
            Type:int
        :param asset:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param type_: No description.
            Type:str
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Delegation History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/asset/custody/transfer-history",
            params={
                "email": email,
                "startTime": startTime,
                "endTime": endTime,
                "asset": asset,
                "timestamp": timestamp,
                "signature": signature,
                "type": type_,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_capital_deposit_address_list_(
        self,
        coin: str,
        timestamp: int,
        signature: str,
        network: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Fetch deposit address list with network (USER_DATA)
        Parameters:
        :param coin: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param network: No description.
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Coin address
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/capital/deposit/address/list",
            params={
                "coin": coin,
                "timestamp": timestamp,
                "signature": signature,
                "network": network,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_spot_delist_schedule(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get symbols delist schedule for spot (MARKET_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Symbols delist schedule
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/spot/delist-schedule",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_capital_withdraw_address_list_(
        self,
    ) -> Dict[str, Any]:
        """
        Fetch withdraw address list (USER_DATA).
        :returns: Withdraw address list
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/capital/withdraw/address/list",
        )

    def get_sapi_account_info(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Account info (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Account info detail
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/account/info",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_status(
        self,
        timestamp: int,
        signature: str,
        optionalSubAccountEmail: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Sub-account's Status on Margin/Futures (For Master Account)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalSubAccountEmail: Sub-account email
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Status on Margin/Futures
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/sub-account/status",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalSubAccountEmail": optionalSubAccountEmail,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_sub_account_margin_enable(
        self,
        subAccountEmail: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Enable Margin for Sub-account (For Master Account)
        Parameters:
        :param subAccountEmail: Sub-account email
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Margin status
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/sub-account/margin/enable",
            params={
                "subAccountEmail": subAccountEmail,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_margin_account(
        self,
        subAccountEmail: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Detail on Sub-account's Margin Account (For Master Account)
        Parameters:
        :param subAccountEmail: Sub-account email
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Margin sub-account details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/sub-account/margin/account",
            params={
                "subAccountEmail": subAccountEmail,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_margin_account_summary(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Summary of Sub-account's Margin Account (For Master Account)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Margin sub-account details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/sub-account/margin/accountSummary",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_sub_account_futures_enable(
        self,
        subAccountEmail: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Enable Futures for Sub-account (For Master Account)
        Parameters:
        :param subAccountEmail: Sub-account email
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Futures status
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/sub-account/futures/enable",
            params={
                "subAccountEmail": subAccountEmail,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_v1_sub_account_futures_account(
        self,
        email: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Detail on Sub-account's Futures Account (For Master Account)
        Parameters:
        :param email: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Futures account details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/sub-account/futures/account",
            params={
                "email": email,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_v1_sub_account_futures_position_risk(
        self,
        subAccountEmail: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Futures Position-Risk of Sub-account (For Master Account)
        Parameters:
        :param subAccountEmail: Sub-account email
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Futures account summary
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/sub-account/futures/positionRisk",
            params={
                "subAccountEmail": subAccountEmail,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_sub_account_futures_transfer(
        self,
        subAccountEmail: str,
        asset: str,
        amount: float,
        type_: int,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Transfer for Sub-account (For Master Account)
                Parameters:
                :param subAccountEmail: Sub-account email
                    Type: str
                :param asset:
                    Type: str
                :param amount:
                    Type: float
                :param type_: * `1` - transfer from subaccount's spot account to its USDT-margined futures account
        * `2` - transfer from subaccount's USDT-margined futures account to its spot account
        * `3` - transfer from subaccount's spot account to its COIN-margined futures account
        * `4` - transfer from subaccount's COIN-margined futures account to its spot account
                    Type:int
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Transfer id
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/sub-account/futures/transfer",
            params={
                "subAccountEmail": subAccountEmail,
                "asset": asset,
                "amount": amount,
                "type": type_,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_sub_account_margin_transfer(
        self,
        subAccountEmail: str,
        asset: str,
        amount: float,
        type_: int,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Margin Transfer for Sub-account (For Master Account)
                Parameters:
                :param subAccountEmail: Sub-account email
                    Type: str
                :param asset:
                    Type: str
                :param amount:
                    Type: float
                :param type_: * `1` - transfer from subaccount's spot account to margin account
        * `2` - transfer from subaccount's margin account to its spot account
                    Type:int
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Transfer id
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/sub-account/margin/transfer",
            params={
                "subAccountEmail": subAccountEmail,
                "asset": asset,
                "amount": amount,
                "type": type_,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_sub_account_transfer_sub_to_sub(
        self,
        subAccountToEmail: str,
        asset: str,
        amount: float,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Transfer to Sub-account of Same Master (For Sub-account)
        Parameters:
        :param subAccountToEmail: Recipient email
            Type: str
        :param asset:
            Type: str
        :param amount:
            Type: float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Transfer id
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/sub-account/transfer/subToSub",
            params={
                "subAccountToEmail": subAccountToEmail,
                "asset": asset,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_sub_account_transfer_sub_to_master(
        self,
        asset: str,
        amount: float,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Transfer to Master (For Sub-account)
        Parameters:
        :param asset:
            Type: str
        :param amount:
            Type: float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Transfer id
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/sub-account/transfer/subToMaster",
            params={
                "asset": asset,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_transfer_sub_user_history(
        self,
        timestamp: int,
        signature: str,
        optionalAsset: str = None,
        type_: int = None,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Sub-account Transfer History (For Sub-account)
                Parameters:
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param optionalAsset:
                    Type: str
                :param type_: * `1` - transfer in
        * `2` - transfer out
                    Type:int
                :param startTime: UTC timestamp in ms
                    Type: int
                :param endTime: UTC timestamp in ms
                    Type: int
                :param limit: Default 500; max 1000.
                    Type: int
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Transfer id
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/sub-account/transfer/subUserHistory",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalAsset": optionalAsset,
                "type": type_,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_universal_transfer(
        self,
        timestamp: int,
        signature: str,
        optionalSubAccountFromEmail: str = None,
        optionalSubAccountToEmail: str = None,
        clientTranId: str = None,
        startTime: int = None,
        endTime: int = None,
        page: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Universal Transfer History (For Master Account)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalSubAccountFromEmail: Sub-account email
            Type: str
        :param optionalSubAccountToEmail: Sub-account email
            Type: str
        :param clientTranId:
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param page: Default 1
            Type: int
        :param limit: Default 500, Max 500
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Transfer History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/sub-account/universalTransfer",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalSubAccountFromEmail": optionalSubAccountFromEmail,
                "optionalSubAccountToEmail": optionalSubAccountToEmail,
                "clientTranId": clientTranId,
                "startTime": startTime,
                "endTime": endTime,
                "page": page,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_sub_account_universal_transfer(
        self,
        fromAccountType: str,
        toAccountType: str,
        asset: str,
        amount: float,
        timestamp: int,
        signature: str,
        optionalSubAccountFromEmail: str = None,
        optionalSubAccountToEmail: str = None,
        clientTranId: str = None,
        symbol: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Universal Transfer (For Master Account)
        Parameters:
        :param fromAccountType: No description.
            Type:str
        :param toAccountType: No description.
            Type:str
        :param asset:
            Type: str
        :param amount:
            Type: float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalSubAccountFromEmail: Sub-account email
            Type: str
        :param optionalSubAccountToEmail: Sub-account email
            Type: str
        :param clientTranId:
            Type: str
        :param symbol: Only supported under ISOLATED_MARGIN type
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Transfer id
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/sub-account/universalTransfer",
            params={
                "fromAccountType": fromAccountType,
                "toAccountType": toAccountType,
                "asset": asset,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "optionalSubAccountFromEmail": optionalSubAccountFromEmail,
                "optionalSubAccountToEmail": optionalSubAccountToEmail,
                "clientTranId": clientTranId,
                "symbol": symbol,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_futures_account(
        self,
        subAccountEmail: str,
        futuresType: int,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Detail on Sub-account's Futures Account V2 (For Master Account)
                Parameters:
                :param subAccountEmail: Sub-account email
                    Type: str
                :param futuresType: * `1` - USDT Margined Futures
        * `2` - COIN Margined Futures
                    Type:int
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: USDT or COIN Margined Futures Details
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v2/sub-account/futures/account",
            params={
                "subAccountEmail": subAccountEmail,
                "futuresType": futuresType,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_futures_account_summary(
        self,
        futuresType: int,
        timestamp: int,
        signature: str,
        page: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Summary of Sub-account's Futures Account V2 (For Master Account)
                Parameters:
                :param futuresType: * `1` - USDT Margined Futures
        * `2` - COIN Margined Futures
                    Type:int
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param page: Default 1
                    Type: int
                :param limit: Default 10, Max 20
                    Type:int
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: USDT or COIN Margined Futures Summary
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v2/sub-account/futures/accountSummary",
            params={
                "futuresType": futuresType,
                "timestamp": timestamp,
                "signature": signature,
                "page": page,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_futures_position_risk(
        self,
        subAccountEmail: str,
        futuresType: int,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Futures Position-Risk of Sub-account V2 (For Master Account)
                Parameters:
                :param subAccountEmail: Sub-account email
                    Type: str
                :param futuresType: * `1` - USDT Margined Futures
        * `2` - COIN Margined Futures
                    Type:int
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: USDT or COIN Margined Futures Position Risk
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v2/sub-account/futures/positionRisk",
            params={
                "subAccountEmail": subAccountEmail,
                "futuresType": futuresType,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_sub_account_blvt_enable(
        self,
        subAccountEmail: str,
        enableBlvt: bool,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Enable Leverage Token for Sub-account (For Master Account)
        Parameters:
        :param subAccountEmail: Sub-account email
            Type: str
        :param enableBlvt: Only true for now
            Type:bool
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: BLVT status
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/sub-account/blvt/enable",
            params={
                "subAccountEmail": subAccountEmail,
                "enableBlvt": enableBlvt,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_managed_subaccount_deposit(
        self,
        subAccountToEmail: str,
        asset: str,
        amount: float,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Deposit assets into the managed sub-account(For Investor Master Account)
        Parameters:
        :param subAccountToEmail: Recipient email
            Type: str
        :param asset:
            Type: str
        :param amount:
            Type: float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Transfer id
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/managed-subaccount/deposit",
            params={
                "subAccountToEmail": subAccountToEmail,
                "asset": asset,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_managed_subaccount_asset(
        self,
        subAccountEmail: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Managed sub-account asset details(For Investor Master Account)
        Parameters:
        :param subAccountEmail: Sub-account email
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of asset details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/managed-subaccount/asset",
            params={
                "subAccountEmail": subAccountEmail,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_managed_subaccount_withdraw(
        self,
        subAccountFromEmail: str,
        asset: str,
        amount: float,
        timestamp: int,
        signature: str,
        transferDate: pd.Timestamp = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Withdrawl assets from the managed sub-account(For Investor Master Account)
        Parameters:
        :param subAccountFromEmail: Sender email
            Type: str
        :param asset:
            Type: str
        :param amount:
            Type: float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param transferDate: Withdrawals is automatically occur on the transfer date(UTC0). If a date is not selected, the withdrawal occurs right now
            Type:Date
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Transfer id
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/managed-subaccount/withdraw",
            params={
                "subAccountFromEmail": subAccountFromEmail,
                "asset": asset,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "transferDate": transferDate,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_managed_subaccount_account_snapshot(
        self,
        subAccountEmail: str,
        type_: str,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Managed sub-account snapshot (For Investor Master Account)
        Parameters:
        :param subAccountEmail: Sub-account email
            Type: str
        :param type_: "SPOT", "MARGIN"(cross), "FUTURES"(UM)
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param limit: min 7, max 30, default 7
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Sub-account spot snapshot
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/managed-subaccount/accountSnapshot",
            params={
                "subAccountEmail": subAccountEmail,
                "type": type_,
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_managed_subaccount_query_trans_log_for_investor(
        self,
        email: str,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        page: int = None,
        limit: int = None,
        transfers: str = None,
        transferFunctionAccountType: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Managed Sub Account Transfer Log (For Investor Master Account)
        Parameters:
        :param email:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param page: Default 1
            Type: int
        :param limit: Default 500; max 1000.
            Type: int
        :param transfers: Transfer Direction (FROM/TO)
            Type:str
        :param transferFunctionAccountType: Transfer function account type (SPOT/MARGIN/ISOLATED_MARGIN/USDT_FUTURE/COIN_FUTURE)
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Managed sub account transfer logs (for invest account)
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/managed-subaccount/queryTransLogForInvestor",
            params={
                "email": email,
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "page": page,
                "limit": limit,
                "transfers": transfers,
                "transferFunctionAccountType": transferFunctionAccountType,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_managed_subaccount_query_trans_log_for_trade_parent(
        self,
        email: str,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        page: int = None,
        limit: int = None,
        transfers: str = None,
        transferFunctionAccountType: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Managed Sub Account Transfer Log (For Trading Team Master Account)
        Parameters:
        :param email:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param page: Default 1
            Type: int
        :param limit: Default 500; max 1000.
            Type: int
        :param transfers: Transfer Direction (FROM/TO)
            Type:str
        :param transferFunctionAccountType: Transfer function account type (SPOT/MARGIN/ISOLATED_MARGIN/USDT_FUTURE/COIN_FUTURE)
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Managed sub account transfer logs (for trading team)
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/managed-subaccount/queryTransLogForTradeParent",
            params={
                "email": email,
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "page": page,
                "limit": limit,
                "transfers": transfers,
                "transferFunctionAccountType": transferFunctionAccountType,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_managed_subaccount_fetch_future_asset(
        self,
        email: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Managed Sub-account Futures Asset Details (For Investor Master Account)
        Parameters:
        :param email:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Sub account futures assset details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/managed-subaccount/fetch-future-asset",
            params={
                "email": email,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_managed_subaccount_margin_asset(
        self,
        email: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Managed Sub-account Margin Asset Details (For Investor Master Account)
        Parameters:
        :param email:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Sub account margin assset details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/managed-subaccount/marginAsset",
            params={
                "email": email,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_managed_subaccount_info(
        self,
        email: str,
        timestamp: int,
        signature: str,
        page: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Managed Sub-account List (For Investor)
        Parameters:
        :param email:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param page: Default 1
            Type: int
        :param limit: Default 500; max 1000.
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Managed sub account list
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/managed-subaccount/info",
            params={
                "email": email,
                "timestamp": timestamp,
                "signature": signature,
                "page": page,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_managed_subaccount_deposit_address(
        self,
        email: str,
        coin: str,
        timestamp: int,
        signature: str,
        network: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Managed Sub-account Deposit Address (For Investor Master Account)
        Parameters:
        :param email:
            Type: str
        :param coin: Coin name
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param network:
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Managed sub deposit address
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/managed-subaccount/deposit/address",
            params={
                "email": email,
                "coin": coin,
                "timestamp": timestamp,
                "signature": signature,
                "network": network,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_managed_subaccount_query_trans_log(
        self,
        transfers: str,
        transferFunctionAccountType: str,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        page: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Managed Sub Account Transfer Log (For Trading Team Sub Account)(USER_DATA)
        Parameters:
        :param transfers: Transfer Direction
            Type:str
        :param transferFunctionAccountType: Transfer function account type
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param page: Default 1
            Type: int
        :param limit: Default 500; max 1000.
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Managed sub deposit address
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/managed-subaccount/query-trans-log",
            params={
                "transfers": transfers,
                "transferFunctionAccountType": transferFunctionAccountType,
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "page": page,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_sub_account_api_ip_restriction(
        self,
        subAccountEmail: str,
        subAccountApiKey: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get IP Restriction for a Sub-account API Key (For Master Account)
        Parameters:
        :param subAccountEmail: Sub-account email
            Type: str
        :param subAccountApiKey:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: IP Restriction information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/sub-account/subAccountApi/ipRestriction",
            params={
                "subAccountEmail": subAccountEmail,
                "subAccountApiKey": subAccountApiKey,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def delete_sapi_sub_account_sub_account_api_ip_restriction_ip_list(
        self,
        subAccountEmail: str,
        subAccountApiKey: str,
        timestamp: int,
        signature: str,
        optionalIpAddress: str = None,
        thirdPartyName: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Delete IP List for a Sub-account API Key (For Master Account)
        Parameters:
        :param subAccountEmail: Sub-account email
            Type: str
        :param subAccountApiKey:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalIpAddress: Can be added in batches, separated by commas
            Type: str
        :param thirdPartyName: third party IP list name
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Delete IP information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="DELETE",
            path="/sapi/v1/sub-account/subAccountApi/ipRestriction/ipList",
            params={
                "subAccountEmail": subAccountEmail,
                "subAccountApiKey": subAccountApiKey,
                "timestamp": timestamp,
                "signature": signature,
                "optionalIpAddress": optionalIpAddress,
                "thirdPartyName": thirdPartyName,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_sub_account_transaction_statistics(
        self,
        email: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Sub-account Transaction Statistics (For Master Account)
        Parameters:
        :param email:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Sub account transaction statistics
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/sub-account/transaction-statistics",
            params={
                "email": email,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_sub_account_eoptions_enable(
        self,
        email: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Enable Options for Sub-account (For Master Account)(USER_DATA)
        Parameters:
        :param email:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Sub account EOptions status
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/sub-account/eoptions/enable",
            params={
                "email": email,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_sub_account_sub_account_api_ip_restriction(
        self,
        subAccountEmail: str,
        subAccountApiKey: str,
        status: str,
        timestamp: int,
        signature: str,
        thirdPartyName: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Update IP Restriction for Sub-Account API key (For Master Account)
        Parameters:
        :param subAccountEmail: Sub-account email
            Type: str
        :param subAccountApiKey:
            Type: str
        :param status: IP Restriction status. 1 = IP Unrestricted. 2 = Restrict access to trusted IPs only. 3 = Restrict access to users' trusted third party IPs only
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param thirdPartyName: third party IP list name
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Update IP Restriction
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v2/sub-account/subAccountApi/ipRestriction",
            params={
                "subAccountEmail": subAccountEmail,
                "subAccountApiKey": subAccountApiKey,
                "status": status,
                "timestamp": timestamp,
                "signature": signature,
                "thirdPartyName": thirdPartyName,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_v4_sub_account_assets(
        self,
        email: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Sub-account Assets (For Master Account)
        Parameters:
        :param email:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Sub account balances
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v4/sub-account/assets",
            params={
                "email": email,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_api_user_data_stream(
        self,
    ) -> Dict[str, Any]:
        """
        Create a ListenKey (USER_STREAM).
        :returns: Listen key
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/api/v3/userDataStream",
        )

    def put_api_user_data_stream(
        self,
        listenKey: str = None,
    ) -> Dict[str, Any]:
        """
        Ping/Keep-alive a ListenKey (USER_STREAM)
        Parameters:
        :param listenKey: User websocket listen key
            Type: str.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="PUT",
            path="/api/v3/userDataStream",
            params={
                "listenKey": listenKey,
            },
        )

    def delete_api_user_data_stream(
        self,
        listenKey: str = None,
    ) -> Dict[str, Any]:
        """
        Close a ListenKey (USER_STREAM)
        Parameters:
        :param listenKey: User websocket listen key
            Type: str.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="DELETE",
            path="/api/v3/userDataStream",
            params={
                "listenKey": listenKey,
            },
        )

    def post_sapi_user_data_stream(
        self,
    ) -> Dict[str, Any]:
        """
        Create a ListenKey (USER_STREAM).
        :returns: Margin listen key
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/userDataStream",
        )

    def put_sapi_user_data_stream(
        self,
        listenKey: str = None,
    ) -> Dict[str, Any]:
        """
        Ping/Keep-alive a ListenKey (USER_STREAM)
        Parameters:
        :param listenKey: User websocket listen key
            Type: str.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="PUT",
            path="/sapi/v1/userDataStream",
            params={
                "listenKey": listenKey,
            },
        )

    def delete_sapi_user_data_stream(
        self,
        listenKey: str = None,
    ) -> Dict[str, Any]:
        """
        Close a ListenKey (USER_STREAM)
        Parameters:
        :param listenKey: User websocket listen key
            Type: str.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="DELETE",
            path="/sapi/v1/userDataStream",
            params={
                "listenKey": listenKey,
            },
        )

    def post_sapi_user_data_stream_isolated(
        self,
    ) -> Dict[str, Any]:
        """
        Generate a Listen Key (USER_STREAM).
        :returns: Isolated margin listen key
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/userDataStream/isolated",
        )

    def put_sapi_user_data_stream_isolated(
        self,
        listenKey: str = None,
    ) -> Dict[str, Any]:
        """
        Ping/Keep-alive a Listen Key (USER_STREAM)
        Parameters:
        :param listenKey: User websocket listen key
            Type: str.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="PUT",
            path="/sapi/v1/userDataStream/isolated",
            params={
                "listenKey": listenKey,
            },
        )

    def delete_sapi_user_data_stream_isolated(
        self,
        listenKey: str = None,
    ) -> Dict[str, Any]:
        """
        Close a ListenKey (USER_STREAM)
        Parameters:
        :param listenKey: User websocket listen key
            Type: str.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="DELETE",
            path="/sapi/v1/userDataStream/isolated",
            params={
                "listenKey": listenKey,
            },
        )

    def get_sapi_fiat_orders(
        self,
        transactionType: int,
        timestamp: int,
        signature: str,
        beginTime: int = None,
        endTime: int = None,
        page: int = None,
        rows: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Fiat Deposit/Withdraw History (USER_DATA)
                Parameters:
                :param transactionType: * `0` - deposit
        * `1` - withdraw
                    Type: int
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param beginTime:
                    Type: int
                :param endTime: UTC timestamp in ms
                    Type: int
                :param page: Default 1
                    Type: int
                :param rows: Default 100, max 500
                    Type: int
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: History of deposit/withdraw orders
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/fiat/orders",
            params={
                "transactionType": transactionType,
                "timestamp": timestamp,
                "signature": signature,
                "beginTime": beginTime,
                "endTime": endTime,
                "page": page,
                "rows": rows,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_fiat_payments(
        self,
        transactionType: int,
        timestamp: int,
        signature: str,
        beginTime: int = None,
        endTime: int = None,
        page: int = None,
        rows: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Fiat Payments History (USER_DATA)
                Parameters:
                :param transactionType: * `0` - deposit
        * `1` - withdraw
                    Type: int
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param beginTime:
                    Type: int
                :param endTime: UTC timestamp in ms
                    Type: int
                :param page: Default 1
                    Type: int
                :param rows: Default 100, max 500
                    Type: int
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: History of fiat payments
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/fiat/payments",
            params={
                "transactionType": transactionType,
                "timestamp": timestamp,
                "signature": signature,
                "beginTime": beginTime,
                "endTime": endTime,
                "page": page,
                "rows": rows,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_lending_project_list_(
        self,
        fixedAndActivityProductType: str,
        timestamp: int,
        signature: str,
        optionalAsset: str = None,
        optionalFixedAndActivityProductStatus: str = None,
        isSortAsc: bool = None,
        sortBy: str = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Fixed/Activity Project List(USER_DATA)
        Parameters:
        :param fixedAndActivityProductType:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalAsset:
            Type: str
        :param optionalFixedAndActivityProductStatus: Default `ALL`
            Type: str
        :param isSortAsc: default "true"
            Type: bool
        :param sortBy: Default `START_TIME`
            Type: str
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of fixed projects
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/lending/project/list",
            params={
                "fixedAndActivityProductType": fixedAndActivityProductType,
                "timestamp": timestamp,
                "signature": signature,
                "optionalAsset": optionalAsset,
                "optionalFixedAndActivityProductStatus": optionalFixedAndActivityProductStatus,
                "isSortAsc": isSortAsc,
                "sortBy": sortBy,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_lending_customized_fixed_purchase(
        self,
        projectId: str,
        lot: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Purchase Fixed/Activity Project (USER_DATA)
        Parameters:
        :param projectId:
            Type: str
        :param lot:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Generated Purchase Id
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/lending/customizedFixed/purchase",
            params={
                "projectId": projectId,
                "lot": lot,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_lending_project_position_list_(
        self,
        asset: str,
        timestamp: int,
        signature: str,
        fixedAndActivityProjectId: str = None,
        optionalFixedAndActivityProductStatus: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Fixed/Activity Project Position (USER_DATA)
        Parameters:
        :param asset:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param fixedAndActivityProjectId:
            Type: str
        :param optionalFixedAndActivityProductStatus: Default `ALL`
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of fixed project positions
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/lending/project/position/list",
            params={
                "asset": asset,
                "timestamp": timestamp,
                "signature": signature,
                "fixedAndActivityProjectId": fixedAndActivityProjectId,
                "optionalFixedAndActivityProductStatus": optionalFixedAndActivityProductStatus,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_lending_position_changed(
        self,
        projectId: str,
        lot: str,
        timestamp: int,
        signature: str,
        optionalPositionId: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Change Fixed/Activity Position to Daily Position (USER_DATA)
        Parameters:
        :param projectId:
            Type: str
        :param lot:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalPositionId:
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Purchase information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/lending/positionChanged",
            params={
                "projectId": projectId,
                "lot": lot,
                "timestamp": timestamp,
                "signature": signature,
                "optionalPositionId": optionalPositionId,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_mining_pub_algo_list(
        self,
    ) -> Dict[str, Any]:
        """
        Acquiring Algorithm (MARKET_DATA).
        :returns: Algorithm information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/mining/pub/algoList",
        )

    def get_sapi_mining_pub_coin_list(
        self,
    ) -> Dict[str, Any]:
        """
        Acquiring CoinName (MARKET_DATA).
        :returns: Coin information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/mining/pub/coinList",
        )

    def get_sapi_mining_worker_detail(
        self,
        algo: str,
        userName: str,
        workerName: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Request for Detail Miner List (USER_DATA)
        Parameters:
        :param algo: Algorithm(sha256)
            Type: str
        :param userName: Mining Account
            Type: str
        :param workerName: Miner’s name
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of workers' hashrates'
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/mining/worker/detail",
            params={
                "algo": algo,
                "userName": userName,
                "workerName": workerName,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_mining_worker_list_(
        self,
        algo: str,
        userName: str,
        timestamp: int,
        signature: str,
        pageIndex: int = None,
        sort: int = None,
        sortColumn: int = None,
        workerStatus: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Request for Miner List (USER_DATA)
        Parameters:
        :param algo: Algorithm(sha256)
            Type: str
        :param userName: Mining Account
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param pageIndex: Page number, default is first page, start form 1
            Type: int
        :param sort: sort sequence(default=0)0 positive sequence, 1 negative sequence
            Type: int
        :param sortColumn: Sort by( default 1): 1: miner name, 2: real-time computing power, 3: daily average computing power, 4: real-time rejection rate, 5: last submission time
            Type: int
        :param workerStatus: miners status(default=0)0 all, 1 valid, 2 invalid, 3 failure
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of workers
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/mining/worker/list",
            params={
                "algo": algo,
                "userName": userName,
                "timestamp": timestamp,
                "signature": signature,
                "pageIndex": pageIndex,
                "sort": sort,
                "sortColumn": sortColumn,
                "workerStatus": workerStatus,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_mining_payment_list_(
        self,
        algo: str,
        userName: str,
        timestamp: int,
        signature: str,
        optionalCoin: str = None,
        startDate: str = None,
        endDate: str = None,
        pageIndex: int = None,
        pageSize: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Earnings List (USER_DATA)
        Parameters:
        :param algo: Algorithm(sha256)
            Type: str
        :param userName: Mining Account
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalCoin: Coin name
            Type: str
        :param startDate: Search date, millisecond timestamp, while empty query all
            Type: str
        :param endDate: Search date, millisecond timestamp, while empty query all
            Type: str
        :param pageIndex: Page number, default is first page, start form 1
            Type: int
        :param pageSize: Number of pages, minimum 10, maximum 200
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of earnings
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/mining/payment/list",
            params={
                "algo": algo,
                "userName": userName,
                "timestamp": timestamp,
                "signature": signature,
                "optionalCoin": optionalCoin,
                "startDate": startDate,
                "endDate": endDate,
                "pageIndex": pageIndex,
                "pageSize": pageSize,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_mining_payment_other(
        self,
        algo: str,
        userName: str,
        timestamp: int,
        signature: str,
        optionalCoin: str = None,
        startDate: str = None,
        endDate: str = None,
        pageIndex: int = None,
        pageSize: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Extra Bonus List (USER_DATA)
        Parameters:
        :param algo: Algorithm(sha256)
            Type: str
        :param userName: Mining Account
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalCoin: Coin name
            Type: str
        :param startDate: Search date, millisecond timestamp, while empty query all
            Type: str
        :param endDate: Search date, millisecond timestamp, while empty query all
            Type: str
        :param pageIndex: Page number, default is first page, start form 1
            Type: int
        :param pageSize: Number of pages, minimum 10, maximum 200
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of extra bonuses
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/mining/payment/other",
            params={
                "algo": algo,
                "userName": userName,
                "timestamp": timestamp,
                "signature": signature,
                "optionalCoin": optionalCoin,
                "startDate": startDate,
                "endDate": endDate,
                "pageIndex": pageIndex,
                "pageSize": pageSize,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_mining_hash_transfer_config_details_list_(
        self,
        timestamp: int,
        signature: str,
        pageIndex: int = None,
        pageSize: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Hashrate Resale List (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param pageIndex: Page number, default is first page, start form 1
            Type: int
        :param pageSize: Number of pages, minimum 10, maximum 200
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of hashrate resales
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/mining/hash-transfer/config/details/list",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "pageIndex": pageIndex,
                "pageSize": pageSize,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_mining_hash_transfer_profit_details(
        self,
        configId: str,
        userName: str,
        timestamp: int,
        signature: str,
        pageIndex: int = None,
        pageSize: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Hashrate Resale Details (USER_DATA)
        Parameters:
        :param configId: Mining ID
            Type: str
        :param userName: Mining Account
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param pageIndex: Page number, default is first page, start form 1
            Type: int
        :param pageSize: Number of pages, minimum 10, maximum 200
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of hashrate resale details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/mining/hash-transfer/profit/details",
            params={
                "configId": configId,
                "userName": userName,
                "timestamp": timestamp,
                "signature": signature,
                "pageIndex": pageIndex,
                "pageSize": pageSize,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_mining_hash_transfer_config(
        self,
        userName: str,
        algo: str,
        toPoolUser: str,
        hashRate: str,
        timestamp: int,
        signature: str,
        startDate: str = None,
        endDate: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Hashrate Resale Request (USER_DATA)
        Parameters:
        :param userName: Mining Account
            Type: str
        :param algo: Algorithm(sha256)
            Type: str
        :param toPoolUser: Mining Account
            Type: str
        :param hashRate: Resale hashrate h/s must be transferred (BTC is greater than 500000000000 ETH is greater than 500000)
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startDate: Search date, millisecond timestamp, while empty query all
            Type: str
        :param endDate: Search date, millisecond timestamp, while empty query all
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Mining Account Id
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/mining/hash-transfer/config",
            params={
                "userName": userName,
                "algo": algo,
                "toPoolUser": toPoolUser,
                "hashRate": hashRate,
                "timestamp": timestamp,
                "signature": signature,
                "startDate": startDate,
                "endDate": endDate,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_mining_hash_transfer_config_cancel(
        self,
        configId: str,
        userName: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Cancel Hashrate Resale configuration (USER_DATA)
        Parameters:
        :param configId: Mining ID
            Type: str
        :param userName: Mining Account
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Success flag
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/mining/hash-transfer/config/cancel",
            params={
                "configId": configId,
                "userName": userName,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_mining_statistics_user_status(
        self,
        algo: str,
        userName: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Statistic List (USER_DATA)
        Parameters:
        :param algo: Algorithm(sha256)
            Type: str
        :param userName: Mining Account
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Mining account statistics
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/mining/statistics/user/status",
            params={
                "algo": algo,
                "userName": userName,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_mining_statistics_user_list_(
        self,
        algo: str,
        userName: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Account List (USER_DATA)
        Parameters:
        :param algo: Algorithm(sha256)
            Type: str
        :param userName: Mining Account
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of mining accounts
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/mining/statistics/user/list",
            params={
                "algo": algo,
                "userName": userName,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_mining_payment_uid(
        self,
        algo: str,
        timestamp: int,
        signature: str,
        startDate: str = None,
        endDate: str = None,
        pageIndex: int = None,
        pageSize: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Mining Account Earning (USER_DATA)
        Parameters:
        :param algo: Algorithm(sha256)
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startDate: Search date, millisecond timestamp, while empty query all
            Type: str
        :param endDate: Search date, millisecond timestamp, while empty query all
            Type: str
        :param pageIndex: Page number, default is first page, start form 1
            Type: int
        :param pageSize: Number of pages, minimum 10, maximum 200
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Mining account earnings
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/mining/payment/uid",
            params={
                "algo": algo,
                "timestamp": timestamp,
                "signature": signature,
                "startDate": startDate,
                "endDate": endDate,
                "pageIndex": pageIndex,
                "pageSize": pageSize,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_futures_transfer(
        self,
        asset: str,
        amount: float,
        type_: int,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        New Future Account Transfer (USER_DATA)
        Parameters:
        :param asset:
            Type: str
        :param amount:
            Type: float
        :param type_: 1: transfer from spot account to USDT-Ⓜ futures account. 2: transfer from USDT-Ⓜ futures account to spot account. 3: transfer from spot account to COIN-Ⓜ futures account. 4: transfer from COIN-Ⓜ futures account to spot account.
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Futures Transfer
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/futures/transfer",
            params={
                "asset": asset,
                "amount": amount,
                "type": type_,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_futures_transfer(
        self,
        asset: str,
        startTimeReq: int,
        timestamp: int,
        signature: str,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Future Account Transaction History List (USER_DATA)
        Parameters:
        :param asset:
            Type: str
        :param startTimeReq: UTC timestamp in ms
            Type: int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Futures Transfer Query
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/futures/transfer",
            params={
                "asset": asset,
                "startTimeReq": startTimeReq,
                "timestamp": timestamp,
                "signature": signature,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_futures_hist_data_link(
        self,
        symbol: str,
        dataType: str,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Future TickLevel Orderbook Historical Data Download Link (USER_DATA)
        Parameters:
        :param symbol: No description.
            Type:str
        :param dataType: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: data link
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/futures/histDataLink",
            params={
                "symbol": symbol,
                "dataType": dataType,
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_algo_futures_new_order_vp(
        self,
        symbol: str,
        side: str,
        quantity: float,
        urgency: str,
        timestamp: int,
        signature: str,
        positionSide: str = None,
        clientAlgoId: str = None,
        reduceOnly: bool = None,
        limitPrice: float = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Volume Participation(VP) New Order (TRADE)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param side:
            Type: str
        :param quantity: Quantity of base asset; The notional (quantity * mark price(base asset)) must be more than the equivalent of 10,000 USDT and less than the equivalent of 1,000,000 USDT
            Type:float
        :param urgency: Represent the relative speed of the current execution; ENUM: LOW, MEDIUM, HIGH
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param positionSide: Default BOTH for One-way Mode ; LONG or SHORT for Hedge Mode. It must be sent in Hedge Mode.
            Type: str
        :param clientAlgoId: A unique id among Algo orders (length should be 32 characters)， If it is not sent, we will give default value
            Type:str
        :param reduceOnly: 'true' or 'false'. Default 'false'; Cannot be sent in Hedge Mode; Cannot be sent when you open a position
            Type:bool
        :param limitPrice: Limit price of the order; If it is not sent, will place order by market price by default
            Type:float
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Volume Participation(VP) Order
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/algo/futures/newOrderVp",
            params={
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "urgency": urgency,
                "timestamp": timestamp,
                "signature": signature,
                "positionSide": positionSide,
                "clientAlgoId": clientAlgoId,
                "reduceOnly": reduceOnly,
                "limitPrice": limitPrice,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_algo_futures_new_order_twap(
        self,
        symbol: str,
        side: str,
        quantity: float,
        duration: int,
        timestamp: int,
        signature: str,
        positionSide: str = None,
        clientAlgoId: str = None,
        reduceOnly: bool = None,
        limitPrice: float = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Time-Weighted Average Price(Twap) New Order (TRADE)
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param side:
            Type: str
        :param quantity: Quantity of base asset; The notional (quantity * mark price(base asset)) must be more than the equivalent of 10,000 USDT and less than the equivalent of 1,000,000 USDT
            Type:float
        :param duration: Duration for TWAP orders in seconds. [300, 86400];Less than 5min => defaults to 5 min; Greater than 24h => defaults to 24h
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param positionSide: Default BOTH for One-way Mode ; LONG or SHORT for Hedge Mode. It must be sent in Hedge Mode.
            Type: str
        :param clientAlgoId: A unique id among Algo orders (length should be 32 characters)， If it is not sent, we will give default value
            Type:str
        :param reduceOnly: 'true' or 'false'. Default 'false'; Cannot be sent in Hedge Mode; Cannot be sent when you open a position
            Type:bool
        :param limitPrice: Limit price of the order; If it is not sent, will place order by market price by default
            Type:float
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Time-Weighted Average Price(Twap) New Order
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/algo/futures/newOrderTwap",
            params={
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "duration": duration,
                "timestamp": timestamp,
                "signature": signature,
                "positionSide": positionSide,
                "clientAlgoId": clientAlgoId,
                "reduceOnly": reduceOnly,
                "limitPrice": limitPrice,
                "recvWindow": recvWindow,
            },
        )

    def delete_sapi_algo_futures_order(
        self,
        algoId: int,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Cancel Algo Order(TRADE)
        Parameters:
        :param algoId: Eg. 14511
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Cancelled order
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="DELETE",
            path="/sapi/v1/algo/futures/order",
            params={
                "algoId": algoId,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_algo_futures_open_orders(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Current Algo Open Orders (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Open Algo Orders
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/algo/futures/openOrders",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_algo_futures_historical_orders(
        self,
        timestamp: int,
        signature: str,
        optionalSymbol: str = None,
        optionalSide: str = None,
        startTime: int = None,
        endTime: int = None,
        page: int = None,
        smallPageSize: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Historical Algo Orders (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalSymbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param optionalSide:
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param page: Default 1
            Type: int
        :param smallPageSize: MIN 1, MAX 100; Default 100
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Historical Algo Orders
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/algo/futures/historicalOrders",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalSymbol": optionalSymbol,
                "optionalSide": optionalSide,
                "startTime": startTime,
                "endTime": endTime,
                "page": page,
                "smallPageSize": smallPageSize,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_algo_futures_sub_orders(
        self,
        algoId: int,
        timestamp: int,
        signature: str,
        page: int = None,
        smallPageSize: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Sub Orders (USER_DATA)
        Parameters:
        :param algoId: No description.
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param page: Default 1
            Type: int
        :param smallPageSize: MIN 1, MAX 100; Default 100
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Sub orders
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/algo/futures/subOrders",
            params={
                "algoId": algoId,
                "timestamp": timestamp,
                "signature": signature,
                "page": page,
                "smallPageSize": smallPageSize,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_algo_spot_new_order_twap(
        self,
        symbol: str,
        side: str,
        quantity: float,
        duration: int,
        timestamp: int,
        signature: str,
        clientAlgoId: str = None,
        limitPrice: float = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Time-Weighted Average Price (Twap) New Order
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param side:
            Type: str
        :param quantity:
            Type: float
        :param duration: No description.
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param clientAlgoId: No description.
            Type:str
        :param limitPrice: No description.
            Type:float
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: twap order response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/algo/spot/newOrderTwap",
            params={
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "duration": duration,
                "timestamp": timestamp,
                "signature": signature,
                "clientAlgoId": clientAlgoId,
                "limitPrice": limitPrice,
                "recvWindow": recvWindow,
            },
        )

    def delete_sapi_algo_spot_order(
        self,
        algoId: int,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Cancel Algo Order
        Parameters:
        :param algoId: No description.
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Cancelled twap order response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="DELETE",
            path="/sapi/v1/algo/spot/order",
            params={
                "algoId": algoId,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_algo_spot_open_orders(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Current Algo Open Orders
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: twap open orders
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/algo/spot/openOrders",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_algo_spot_historical_orders(
        self,
        symbol: str,
        side: str,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        page: int = None,
        smallPageSize: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Historical Algo Orders
        Parameters:
        :param symbol: Trading symbol, e.g. BNBUSDT
            Type: str
        :param side:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param page: Default 1
            Type: int
        :param smallPageSize: MIN 1, MAX 100; Default 100
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: twap historical orders
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/algo/spot/historicalOrders",
            params={
                "symbol": symbol,
                "side": side,
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "page": page,
                "smallPageSize": smallPageSize,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_algo_spot_sub_orders(
        self,
        algoId: int,
        timestamp: int,
        signature: str,
        page: int = None,
        smallPageSize: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Sub Orders
        Parameters:
        :param algoId: No description.
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param page: Default 1
            Type: int
        :param smallPageSize: MIN 1, MAX 100; Default 100
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: twap sub orders
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/algo/spot/subOrders",
            params={
                "algoId": algoId,
                "timestamp": timestamp,
                "signature": signature,
                "page": page,
                "smallPageSize": smallPageSize,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_portfolio_account(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Portfolio Margin Account (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Portfolio account.
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/portfolio/account",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_v1_portfolio_collateral_rate(
        self,
    ) -> Dict[str, Any]:
        """
        Portfolio Margin Collateral Rate (MARKET_DATA).
        :returns: Portfolio Margin Collateral Rate.
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/portfolio/collateralRate",
        )

    def get_sapi_portfolio_collateral_rate(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Portfolio Margin Pro Tiered Collateral Rate(USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Portfolio Margin Collateral Rate.
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v2/portfolio/collateralRate",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_portfolio_pm_loan(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Portfolio Margin Bankruptcy Loan Amount (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Portfolio Margin Bankruptcy Loan Amount.
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/portfolio/pmLoan",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_portfolio_repay(
        self,
        timestamp: int,
        signature: str,
        from_: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Portfolio Margin Bankruptcy Loan Repay (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param from_: No description.
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Transaction.
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/portfolio/repay",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "from": from_,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_portfolio_interest_history(
        self,
        asset: str,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Classic Portfolio Margin Negative Balance Interest History (USER_DATA)
        Parameters:
        :param asset:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Balance interest history
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/portfolio/interest-history",
            params={
                "asset": asset,
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_portfolio_asset_index_price(
        self,
        asset: str = None,
    ) -> Dict[str, Any]:
        """
        Query Portfolio Margin Asset Index Price (MARKET_DATA)
        Parameters:
        :param asset: No description.
            Type:str.
        :returns: asset price index
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/portfolio/asset-index-price",
            params={
                "asset": asset,
            },
        )

    def post_sapi_portfolio_auto_collection(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Fund Auto-collection (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/portfolio/auto-collection",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_portfolio_bnb_transfer(
        self,
        transferSide: str,
        amount: float,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        BNB Transfer (USER_DATA)
        Parameters:
        :param transferSide: No description.
            Type:str
        :param amount:
            Type: float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/portfolio/bnb-transfer",
            params={
                "transferSide": transferSide,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_portfolio_repay_futures_switch(
        self,
        autoRepay: bool,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Change Auto-repay-futures Status (USER_DATA)
        Parameters:
        :param autoRepay:
            Type: bool
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/portfolio/repay-futures-switch",
            params={
                "autoRepay": autoRepay,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_portfolio_repay_futures_switch(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Auto-repay-futures Status (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/portfolio/repay-futures-switch",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_portfolio_repay_futures_negative_balance(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Repay futures Negative Balance (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/portfolio/repay-futures-negative-balance",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_portfolio_margin_asset_leverage(
        self,
    ) -> Dict[str, Any]:
        """
        Get Portfolio Margin Asset Leverage (USER_DATA).
        :returns: Classic Portfolio Margin Collateral Rate
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/portfolio/margin-asset-leverage",
        )

    def post_sapi_portfolio_asset_collection(
        self,
        asset: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Fund Collection by Asset (USER_DATA)
        Parameters:
        :param asset:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/portfolio/asset-collection",
            params={
                "asset": asset,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_blvt_token_info(
        self,
        optionalBlvtTokenName: str = None,
    ) -> Dict[str, Any]:
        """
        BLVT Info (MARKET_DATA)
        Parameters:
        :param optionalBlvtTokenName: BTCDOWN, BTCUP
            Type: str.
        :returns: List of token information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/blvt/tokenInfo",
            params={
                "optionalBlvtTokenName": optionalBlvtTokenName,
            },
        )

    def post_sapi_blvt_subscribe(
        self,
        blvtTokenName: str,
        cost: float,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Subscribe BLVT (USER_DATA)
        Parameters:
        :param blvtTokenName: BTCDOWN, BTCUP
            Type: str
        :param cost: Spot balance
            Type:float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Subscription Info
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/blvt/subscribe",
            params={
                "blvtTokenName": blvtTokenName,
                "cost": cost,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_blvt_subscribe_record(
        self,
        timestamp: int,
        signature: str,
        optionalBlvtTokenName: str = None,
        id_: int = None,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Subscription Record (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalBlvtTokenName: BTCDOWN, BTCUP
            Type: str
        :param id_: No description.
            Type:int
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param limit: Default 500; max 1000.
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of subscription record
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/blvt/subscribe/record",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalBlvtTokenName": optionalBlvtTokenName,
                "id": id_,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_blvt_redeem(
        self,
        blvtTokenName: str,
        amount: float,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Redeem BLVT (USER_DATA)
        Parameters:
        :param blvtTokenName: BTCDOWN, BTCUP
            Type: str
        :param amount:
            Type: float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Redemption record
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/blvt/redeem",
            params={
                "blvtTokenName": blvtTokenName,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_blvt_redeem_record(
        self,
        timestamp: int,
        signature: str,
        optionalBlvtTokenName: str = None,
        id_: int = None,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Redemption Record (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalBlvtTokenName: BTCDOWN, BTCUP
            Type: str
        :param id_: No description.
            Type:int
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param limit: default 1000, max 1000
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of redemption record
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/blvt/redeem/record",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalBlvtTokenName": optionalBlvtTokenName,
                "id": id_,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_blvt_user_limit(
        self,
        timestamp: int,
        signature: str,
        optionalBlvtTokenName: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        BLVT User Limit Info (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param optionalBlvtTokenName: BTCDOWN, BTCUP
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: List of token limits
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/blvt/userLimit",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalBlvtTokenName": optionalBlvtTokenName,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_c2c_order_match_list_user_order_history(
        self,
        tradeType: str,
        timestamp: int,
        signature: str,
        startTimestamp: int = None,
        endTimestamp: int = None,
        page: int = None,
        rows: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get C2C Trade History (USER_DATA)
        Parameters:
        :param tradeType: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTimestamp: UTC timestamp in ms
            Type:int
        :param endTimestamp: UTC timestamp in ms
            Type:int
        :param page: Default 1
            Type: int
        :param rows: default 100, max 100
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Trades history
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/c2c/orderMatch/listUserOrderHistory",
            params={
                "tradeType": tradeType,
                "timestamp": timestamp,
                "signature": signature,
                "startTimestamp": startTimestamp,
                "endTimestamp": endTimestamp,
                "page": page,
                "rows": rows,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_vip_ongoing_orders(
        self,
        timestamp: int,
        signature: str,
        orderId: int = None,
        collateralAccountId: int = None,
        loanCoin: str = None,
        collateralCoin: str = None,
        current: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get VIP Loan Ongoing Orders (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: Order id
            Type: int
        :param collateralAccountId: No description.
            Type:int
        :param loanCoin: Coin loaned
            Type: str
        :param collateralCoin: Coin used as collateral
            Type: str
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param limit: Default 10; max 100.
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Ongoing VIP Loan Orders
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/vip/ongoing/orders",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "collateralAccountId": collateralAccountId,
                "loanCoin": loanCoin,
                "collateralCoin": collateralCoin,
                "current": current,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_loan_vip_repay(
        self,
        amount: float,
        timestamp: int,
        signature: str,
        orderId: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        VIP Loan Repay (TRADE)
        Parameters:
        :param amount:
            Type: float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: Order id
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: VIP Loan Repayment
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/loan/vip/repay",
            params={
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_vip_repay_history(
        self,
        timestamp: int,
        signature: str,
        orderId: int = None,
        loanCoin: str = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get VIP Loan Repayment History (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: Order id
            Type: int
        :param loanCoin: Coin loaned
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param limit: Default 10; max 100.
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: VIP Loan Repayment History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/vip/repay/history",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "loanCoin": loanCoin,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_vip_collateral_account(
        self,
        timestamp: int,
        signature: str,
        orderId: int = None,
        collateralAccountId: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Check Locked Value of VIP Collateral Account (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: Order id
            Type: int
        :param collateralAccountId: No description.
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: VIP Locked Value
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/vip/collateral/account",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "collateralAccountId": collateralAccountId,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_loan_vip_borrow(
        self,
        loanAccountId: int,
        loanAmount: float,
        collateralAccountId: str,
        collateralCoin: str,
        isFlexibleRate: str,
        timestamp: int,
        signature: str,
        loanCoin: str = None,
        loanTerm: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        VIP Loan Borrow
        Parameters:
        :param loanAccountId: No description.
            Type:int
        :param loanAmount: No description.
            Type:float
        :param collateralAccountId: No description.
            Type:str
        :param collateralCoin: No description.
            Type:str
        :param isFlexibleRate: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param loanCoin: Coin loaned
            Type: str
        :param loanTerm: No description.
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Collateral Assets Data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/loan/vip/borrow",
            params={
                "loanAccountId": loanAccountId,
                "loanAmount": loanAmount,
                "collateralAccountId": collateralAccountId,
                "collateralCoin": collateralCoin,
                "isFlexibleRate": isFlexibleRate,
                "timestamp": timestamp,
                "signature": signature,
                "loanCoin": loanCoin,
                "loanTerm": loanTerm,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_vip_loanable_data(
        self,
        timestamp: int,
        signature: str,
        loanCoin: str = None,
        vipLevel: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Loanable Assets Data
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param loanCoin: Coin loaned
            Type: str
        :param vipLevel: Defaults to user's vip level
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Loanable Assets Data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/vip/loanable/data",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "loanCoin": loanCoin,
                "vipLevel": vipLevel,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_vip_collateral_data(
        self,
        timestamp: int,
        signature: str,
        collateralCoin: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Collateral Asset Data (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param collateralCoin: Coin used as collateral
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Collateral Asset Data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/vip/collateral/data",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "collateralCoin": collateralCoin,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_vip_request_data(
        self,
        timestamp: int,
        signature: str,
        current: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Application Status (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param limit: Default 500; max 1000.
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Application Status
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/vip/request/data",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "current": current,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_vip_request_interest_rate(
        self,
        timestamp: int,
        signature: str,
        loanCoin: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Borrow Interest Rate (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param loanCoin: Max 10 assets, Multiple split by ","
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Borrow interest rate
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/vip/request/interestRate",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "loanCoin": loanCoin,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_loan_vip_renew(
        self,
        timestamp: int,
        signature: str,
        orderId: int = None,
        loanTerm: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        VIP Loan Renew
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: Order id
            Type: int
        :param loanTerm: No description.
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Loan renew result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/loan/vip/renew",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "loanTerm": loanTerm,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_income(
        self,
        timestamp: int,
        signature: str,
        optionalAsset: str = None,
        type_: str = None,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
              Get Crypto Loans Income History (USER_DATA)
              Parameters:
              :param timestamp: UTC timestamp in ms
                  Type: int
              :param signature: Signature
                  Type: str
              :param optionalAsset:
                  Type: str
              :param type_: All types will be returned by default.
        * `borrowIn`
        * `collateralSpent`
        * `repayAmount`
        * `collateralReturn` - Collateral return after repayment
        * `addCollateral`
        * `removeCollateral`
        * `collateralReturnAfterLiquidation`
                  Type:str
              :param startTime: UTC timestamp in ms
                  Type: int
              :param endTime: UTC timestamp in ms
                  Type: int
              :param limit: default 20, max 100
                  Type:int
              :param recvWindow: The value cannot be greater than 60000
                  Type: int.
              :returns: Loan History
              :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/income",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "optionalAsset": optionalAsset,
                "type": type_,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_loan_borrow(
        self,
        loanCoinReq: str,
        collateralCoinReq: str,
        loanTerm: int,
        timestamp: int,
        signature: str,
        loanAmount: float = None,
        collateralAmount: float = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Crypto Loan Borrow (TRADE)
        Parameters:
        :param loanCoinReq: Coin loaned
            Type: str
        :param collateralCoinReq: Coin used as collateral
            Type: str
        :param loanTerm: 7/14/30/90/180 days
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param loanAmount: Loan amount
            Type: float
        :param collateralAmount:
            Type: float
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Borrow Information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/loan/borrow",
            params={
                "loanCoinReq": loanCoinReq,
                "collateralCoinReq": collateralCoinReq,
                "loanTerm": loanTerm,
                "timestamp": timestamp,
                "signature": signature,
                "loanAmount": loanAmount,
                "collateralAmount": collateralAmount,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_borrow_history(
        self,
        timestamp: int,
        signature: str,
        orderId: int = None,
        loanCoin: str = None,
        collateralCoin: str = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Crypto Loans Borrow History (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: orderId in POST /sapi/v1/loan/borrow
            Type:int
        :param loanCoin: Coin loaned
            Type: str
        :param collateralCoin: Coin used as collateral
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param limit: default 10, max 100
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Borrow History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/borrow/history",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "loanCoin": loanCoin,
                "collateralCoin": collateralCoin,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_ongoing_orders(
        self,
        timestamp: int,
        signature: str,
        orderId: int = None,
        loanCoin: str = None,
        collateralCoin: str = None,
        current: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Loan Ongoing Orders (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: orderId in POST /sapi/v1/loan/borrow
            Type:int
        :param loanCoin: Coin loaned
            Type: str
        :param collateralCoin: Coin used as collateral
            Type: str
        :param current: Current querying page. Start from 1; default:1, max:1000
            Type:int
        :param limit: default 10, max 100
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Ongoing Orders
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/ongoing/orders",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "loanCoin": loanCoin,
                "collateralCoin": collateralCoin,
                "current": current,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_loan_repay(
        self,
        orderId: int,
        amount: float,
        timestamp: int,
        signature: str,
        type_: int = None,
        collateralReturn: bool = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Crypto Loan Repay (TRADE)
        Parameters:
        :param orderId: Order ID
            Type:int
        :param amount: Repayment Amount
            Type:float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param type_: Default: 1. 1 for 'repay with borrowed coin'; 2 for 'repay with collateral'.
            Type:int
        :param collateralReturn: Default: TRUE. TRUE: Return extra collateral to spot account; FALSE: Keep extra collateral in the order.
            Type:bool
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Repayment Information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/loan/repay",
            params={
                "orderId": orderId,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "type": type_,
                "collateralReturn": collateralReturn,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_repay_history(
        self,
        timestamp: int,
        signature: str,
        orderId: int = None,
        loanCoin: str = None,
        collateralCoin: str = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Loan Repayment History (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: Order ID
            Type:int
        :param loanCoin: Coin loaned
            Type: str
        :param collateralCoin: Coin used as collateral
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param limit: default 10, max 100
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Loan Repayment History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/repay/history",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "loanCoin": loanCoin,
                "collateralCoin": collateralCoin,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_loan_adjust_ltv(
        self,
        orderId: int,
        amount: float,
        direction: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Crypto Loan Adjust LTV (TRADE)
        Parameters:
        :param orderId: Order ID
            Type:int
        :param amount: Amount
            Type:float
        :param direction: 'ADDITIONAL', 'REDUCED'
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: LTV Adjust
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/loan/adjust/ltv",
            params={
                "orderId": orderId,
                "amount": amount,
                "direction": direction,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_ltv_adjustment_history(
        self,
        timestamp: int,
        signature: str,
        orderId: int = None,
        loanCoin: str = None,
        collateralCoin: str = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Loan LTV Adjustment History (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: Order ID
            Type:int
        :param loanCoin: Coin loaned
            Type: str
        :param collateralCoin: Coin used as collateral
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param limit: default 10, max 100
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: LTV Adjustment History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/ltv/adjustment/history",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "loanCoin": loanCoin,
                "collateralCoin": collateralCoin,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_loanable_data(
        self,
        timestamp: int,
        signature: str,
        loanCoin: str = None,
        vipLevel: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Loanable Assets Data (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param loanCoin: Coin loaned
            Type: str
        :param vipLevel: Defaults to user's vip level
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Loanable Assets Data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/loanable/data",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "loanCoin": loanCoin,
                "vipLevel": vipLevel,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_collateral_data(
        self,
        timestamp: int,
        signature: str,
        collateralCoin: str = None,
        vipLevel: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Collateral Assets Data (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param collateralCoin: Coin used as collateral
            Type: str
        :param vipLevel: Defaults to user's vip level
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Collateral Assets Data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/collateral/data",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "collateralCoin": collateralCoin,
                "vipLevel": vipLevel,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_repay_collateral_rate(
        self,
        loanCoinReq: str,
        collateralCoinReq: str,
        repayAmount: float,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Check Collateral Repay Rate (USER_DATA)
        Parameters:
        :param loanCoinReq: Coin loaned
            Type: str
        :param collateralCoinReq: Coin used as collateral
            Type: str
        :param repayAmount: repay amount of loanCoin
            Type:float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Collateral Assets Data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/loan/repay/collateral/rate",
            params={
                "loanCoinReq": loanCoinReq,
                "collateralCoinReq": collateralCoinReq,
                "repayAmount": repayAmount,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_loan_customize_margin_call(
        self,
        marginCall: float,
        timestamp: int,
        signature: str,
        orderId: int = None,
        collateralCoin: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Crypto Loan Customize Margin Call (TRADE)
        Parameters:
        :param marginCall: No description.
            Type:float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: Mandatory when collateralCoin is empty. Send either orderId or collateralCoin, if both parameters are sent, take orderId only.
            Type:int
        :param collateralCoin: Coin used as collateral
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Collateral Assets Data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/loan/customize/margin_call",
            params={
                "marginCall": marginCall,
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "collateralCoin": collateralCoin,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_loan_flexible_borrow(
        self,
        timestamp: int,
        signature: str,
        loanCoin: str = None,
        loanAmount: float = None,
        collateralCoin: str = None,
        collateralAmount: float = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Borrow - Flexible Loan Borrow (TRADE)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param loanCoin: Coin loaned
            Type: str
        :param loanAmount: Loan amount
            Type: float
        :param collateralCoin: Coin used as collateral
            Type: str
        :param collateralAmount:
            Type: float
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Collateral Assets Data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v2/loan/flexible/borrow",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "loanCoin": loanCoin,
                "loanAmount": loanAmount,
                "collateralCoin": collateralCoin,
                "collateralAmount": collateralAmount,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_flexible_ongoing_orders(
        self,
        timestamp: int,
        signature: str,
        loanCoin: str = None,
        collateralCoin: str = None,
        current: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Borrow - Get Flexible Loan Ongoing Orders (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param loanCoin: Coin loaned
            Type: str
        :param collateralCoin: Coin used as collateral
            Type: str
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param limit: Default 500; max 1000.
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Collateral Assets Data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v2/loan/flexible/ongoing/orders",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "loanCoin": loanCoin,
                "collateralCoin": collateralCoin,
                "current": current,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_flexible_borrow_history(
        self,
        timestamp: int,
        signature: str,
        loanCoin: str = None,
        collateralCoin: str = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Borrow - Get Flexible Loan Borrow History (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param loanCoin: Coin loaned
            Type: str
        :param collateralCoin: Coin used as collateral
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param limit: Default 500; max 1000.
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Loan borrow histroy
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v2/loan/flexible/borrow/history",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "loanCoin": loanCoin,
                "collateralCoin": collateralCoin,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_loan_flexible_repay(
        self,
        repayAmount: float,
        timestamp: int,
        signature: str,
        loanCoin: str = None,
        collateralCoin: str = None,
        collateralReturn: bool = None,
        fullRepayment: bool = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Repay - Flexible Loan Repay (TRADE)
                Parameters:
                :param repayAmount: repay amount of loanCoin
                    Type:float
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param loanCoin: Coin loaned
                    Type: str
                :param collateralCoin: Coin used as collateral
                    Type: str
                :param collateralReturn: Default: TRUE.
        TRUE: Return extra collateral to earn account;
        FALSE: Keep extra collateral in the order, and lower LTV.
                    Type:bool
                :param fullRepayment: Default: FALSE.
        TRUE: Full repayment;
        FALSE: Partial repayment, based on loanAmount
                    Type:bool
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Loan repay
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v2/loan/flexible/repay",
            params={
                "repayAmount": repayAmount,
                "timestamp": timestamp,
                "signature": signature,
                "loanCoin": loanCoin,
                "collateralCoin": collateralCoin,
                "collateralReturn": collateralReturn,
                "fullRepayment": fullRepayment,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_flexible_repay_history(
        self,
        timestamp: int,
        signature: str,
        loanCoin: str = None,
        collateralCoin: str = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Repay - Get Flexible Loan Repayment History (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param loanCoin: Coin loaned
            Type: str
        :param collateralCoin: Coin used as collateral
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param limit: Default 500; max 1000.
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Loan repay history
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v2/loan/flexible/repay/history",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "loanCoin": loanCoin,
                "collateralCoin": collateralCoin,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_loan_flexible_adjust_ltv(
        self,
        adjustmentAmount: float,
        direction: str,
        timestamp: int,
        signature: str,
        loanCoin: str = None,
        collateralCoin: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Adjust LTV - Flexible Loan Adjust LTV (TRADE)
        Parameters:
        :param adjustmentAmount: No description.
            Type:float
        :param direction: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param loanCoin: Coin loaned
            Type: str
        :param collateralCoin: Coin used as collateral
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: adjust LTV result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v2/loan/flexible/adjust/ltv",
            params={
                "adjustmentAmount": adjustmentAmount,
                "direction": direction,
                "timestamp": timestamp,
                "signature": signature,
                "loanCoin": loanCoin,
                "collateralCoin": collateralCoin,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_flexible_ltv_adjustment_history(
        self,
        timestamp: int,
        signature: str,
        loanCoin: str = None,
        collateralCoin: str = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Adjust LTV - Get Flexible Loan LTV Adjustment History (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param loanCoin: Coin loaned
            Type: str
        :param collateralCoin: Coin used as collateral
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param limit: Default 500; max 1000.
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: LTV adjustment history
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v2/loan/flexible/ltv/adjustment/history",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "loanCoin": loanCoin,
                "collateralCoin": collateralCoin,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_flexible_loanable_data(
        self,
        timestamp: int,
        signature: str,
        loanCoin: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Flexible Loan Assets Data (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param loanCoin: Coin loaned
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Loan asset data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v2/loan/flexible/loanable/data",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "loanCoin": loanCoin,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_loan_flexible_collateral_data(
        self,
        timestamp: int,
        signature: str,
        collateralCoin: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Flexible Loan Collateral Assets Data (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param collateralCoin: Coin used as collateral
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Loan asset data
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v2/loan/flexible/collateral/data",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "collateralCoin": collateralCoin,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_pay_transactions(
        self,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Pay Trade History (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param limit: default 100, max 100
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Pay History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/pay/transactions",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_convert_exchange_info(
        self,
        fromAsset: str = None,
        toAsset: str = None,
    ) -> Dict[str, Any]:
        """
        List All Convert Pairs
        Parameters:
        :param fromAsset: User spends coin
            Type:str
        :param toAsset: User receives coin
            Type:str.
        :returns: List Convert Pairs
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/convert/exchangeInfo",
            params={
                "fromAsset": fromAsset,
                "toAsset": toAsset,
            },
        )

    def get_sapi_convert_asset_info(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query order quantity precision per asset (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Asset Precision Information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/convert/assetInfo",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_convert_get_quote(
        self,
        fromAsset: str,
        toAsset: str,
        timestamp: int,
        signature: str,
        fromAmount: float = None,
        toAmount: float = None,
        validTime: str = None,
        walletType: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Send quote request (USER_DATA)
        Parameters:
        :param fromAsset: No description.
            Type:str
        :param toAsset: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param fromAmount: When specified, it is the amount you will be debited after the conversion
            Type:float
        :param toAmount: When specified, it is the amount you will be debited after the conversion
            Type:float
        :param validTime: 10s, 30s, 1m, 2m, default 10s
            Type:str
        :param walletType: SPOT or FUNDING. Default is SPOT
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Quote Request
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/convert/getQuote",
            params={
                "fromAsset": fromAsset,
                "toAsset": toAsset,
                "timestamp": timestamp,
                "signature": signature,
                "fromAmount": fromAmount,
                "toAmount": toAmount,
                "validTime": validTime,
                "walletType": walletType,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_convert_accept_quote(
        self,
        quoteId: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Accept Quote (TRADE)
        Parameters:
        :param quoteId: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Accept Quote
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/convert/acceptQuote",
            params={
                "quoteId": quoteId,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_convert_order_status(
        self,
        timestamp: int,
        signature: str,
        orderId: str = None,
        quoteId: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Order status (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param orderId: No description.
            Type:str
        :param quoteId: No description.
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Order Status
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/convert/orderStatus",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "orderId": orderId,
                "quoteId": quoteId,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_convert_limit_place_order(
        self,
        baseAsset: str,
        quoteAsset: str,
        limitPrice: float,
        side: str,
        timestamp: int,
        signature: str,
        baseAmount: float = None,
        quoteAmount: float = None,
        walletType: str = None,
        expiredType: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Place limit order (USER_DATA)
        Parameters:
        :param baseAsset:
            Type: str
        :param quoteAsset:
            Type: str
        :param limitPrice: Symbol limit price (from baseAsset to quoteAsset)
            Type:float
        :param side:
            Type: str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param baseAmount: Base asset amount. (One of baseAmount or quoteAmount is required)
            Type:float
        :param quoteAmount: Quote asset amount. (One of baseAmount or quoteAmount is required)
            Type:float
        :param walletType: SPOT or FUNDING or SPOT_FUNDING. It is to use which type of assets. Default is SPOT.
            Type:str
        :param expiredType: 1_D, 3_D, 7_D, 30_D (D means day)
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: None
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/convert/limit/placeOrder",
            params={
                "baseAsset": baseAsset,
                "quoteAsset": quoteAsset,
                "limitPrice": limitPrice,
                "side": side,
                "timestamp": timestamp,
                "signature": signature,
                "baseAmount": baseAmount,
                "quoteAmount": quoteAmount,
                "walletType": walletType,
                "expiredType": expiredType,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_convert_limit_cancel_order(
        self,
        orderId: int,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Cancel limit order (USER_DATA)
        Parameters:
        :param orderId: No description.
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Cancel Order
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/convert/limit/cancelOrder",
            params={
                "orderId": orderId,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_convert_limit_query_open_orders(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query limit open orders (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: All existing limit orders
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/convert/limit/queryOpenOrders",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_convert_trade_flow(
        self,
        startTime: int,
        endTime: int,
        timestamp: int,
        signature: str,
        limit: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Convert Trade History (USER_DATA)
        Parameters:
        :param startTime: UTC timestamp in ms
            Type:int
        :param endTime: UTC timestamp in ms
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param limit: default 100, max 1000
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Convert Trade History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/convert/tradeFlow",
            params={
                "startTime": startTime,
                "endTime": endTime,
                "timestamp": timestamp,
                "signature": signature,
                "limit": limit,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_rebate_tax_query(
        self,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        page: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Spot Rebate History Records (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type:int
        :param endTime: UTC timestamp in ms
            Type:int
        :param page: default 1
            Type:int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Rebate History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/rebate/taxQuery",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "page": page,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_nft_history_transactions(
        self,
        orderType: int,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        limit50: int = None,
        page: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get NFT Transaction History (USER_DATA)
        Parameters:
        :param orderType: 0: purchase order, 1: sell order, 2: royalty income, 3: primary market order, 4: mint fee
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param limit50: Default 50, Max 50
            Type: int
        :param page: Default 1
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: NFT Transaction History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/nft/history/transactions",
            params={
                "orderType": orderType,
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "limit50": limit50,
                "page": page,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_nft_history_deposit(
        self,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        limit50: int = None,
        page: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get NFT Deposit History(USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param limit50: Default 50, Max 50
            Type: int
        :param page: Default 1
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: NFT Deposit History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/nft/history/deposit",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "limit50": limit50,
                "page": page,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_nft_history_withdraw(
        self,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        limit50: int = None,
        page: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get NFT Withdraw History (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param limit50: Default 50, Max 50
            Type: int
        :param page: Default 1
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: NFT Withdraw History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/nft/history/withdraw",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "limit50": limit50,
                "page": page,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_nft_user_get_asset(
        self,
        timestamp: int,
        signature: str,
        limit50: int = None,
        page: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get NFT Asset (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param limit50: Default 50, Max 50
            Type: int
        :param page: Default 1
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Asset Information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/nft/user/getAsset",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "limit50": limit50,
                "page": page,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_giftcard_create_code(
        self,
        token: str,
        amount: float,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Create a Binance Code (USER_DATA)
        Parameters:
        :param token: The coin type contained in the Binance Code
            Type:str
        :param amount: The amount of the coin
            Type:float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Code creation
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/giftcard/createCode",
            params={
                "token": token,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_giftcard_redeem_code(
        self,
        code: str,
        timestamp: int,
        signature: str,
        externalUid: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Redeem a Binance Code (USER_DATA)
        Parameters:
        :param code: Binance Code
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param externalUid: Each external unique ID represents a unique user on the partner platform. The function helps you to identify the redemption behavior of different users, such as redemption frequency and amount. It also helps risk and limit control of a single account, such as daily limit on redemption volume, frequency, and incorrect number of entries. This will also prevent a single user account reach the partner's daily redemption limits. We strongly recommend you to use this feature and transfer us the User ID of your users if you have different users redeeming Binance codes on your platform. To protect user data privacy, you may choose to transfer the user id in any desired format (max. 400 characters).
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Redeemed Information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/giftcard/redeemCode",
            params={
                "code": code,
                "timestamp": timestamp,
                "signature": signature,
                "externalUid": externalUid,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_giftcard_verify(
        self,
        referenceNo: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Verify a Binance Code (USER_DATA)
        Parameters:
        :param referenceNo: reference number
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Code Verification
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/giftcard/verify",
            params={
                "referenceNo": referenceNo,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_giftcard_cryptography_rsa_public_key(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Fetch RSA Public Key (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: RSA Public Key.
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/giftcard/cryptography/rsa-public-key",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_giftcard_buy_code(
        self,
        baseToken: str,
        faceToken: str,
        baseTokenAmount: float,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Buy a Binance Code (TRADE)
        Parameters:
        :param baseToken: The token you want to pay, example BUSD
            Type:str
        :param faceToken: The token you want to buy, example BNB. If faceToken = baseToken, it's the same as createCode endpoint.
            Type:str
        :param baseTokenAmount: The base token asset quantity, example  1.002
            Type:float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Code creation
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/giftcard/buyCode",
            params={
                "baseToken": baseToken,
                "faceToken": faceToken,
                "baseTokenAmount": baseTokenAmount,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_giftcard_buy_code_token_limit(
        self,
        baseToken: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Fetch Token Limit (USER_DATA)
        Parameters:
        :param baseToken: The token you want to pay, example BUSD
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Token limit
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/giftcard/buyCode/token-limit",
            params={
                "baseToken": baseToken,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_lending_auto_invest_target_asset_list_(
        self,
        timestamp: int,
        signature: str,
        targetAsset: str = None,
        size: int = None,
        current: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get target asset list (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param targetAsset: No description.
            Type:str
        :param size: Default:10 Max:100
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Target asset list
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/lending/auto-invest/target-asset/list",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "targetAsset": targetAsset,
                "size": size,
                "current": current,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_lending_auto_invest_target_asset_roi_list_(
        self,
        targetAsset: str,
        hisRoiType: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get target asset ROI data (USER_DATA)
        Parameters:
        :param targetAsset:
            Type: str
        :param hisRoiType: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Target asset list
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/lending/auto-invest/target-asset/roi/list",
            params={
                "targetAsset": targetAsset,
                "hisRoiType": hisRoiType,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_lending_auto_invest_all__asset(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query all source asset and target asset (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Target asset
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/lending/auto-invest/all/asset",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_lending_auto_invest_source_asset_list_(
        self,
        usageType: str,
        timestamp: int,
        signature: str,
        targetAsset: str = None,
        indexId: int = None,
        flexibleAllowedToUse: bool = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query source asset list (USER_DATA)
        Parameters:
        :param usageType: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param targetAsset: No description.
            Type:str
        :param indexId: No description.
            Type:int
        :param flexibleAllowedToUse: No description.
            Type:bool
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Asset list
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/lending/auto-invest/source-asset/list",
            params={
                "usageType": usageType,
                "timestamp": timestamp,
                "signature": signature,
                "targetAsset": targetAsset,
                "indexId": indexId,
                "flexibleAllowedToUse": flexibleAllowedToUse,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_lending_auto_invest_plan_add(
        self,
        sourceType: str,
        planType: str,
        subscriptionAmount: float,
        subscriptionCycle: str,
        subscriptionStartTime: int,
        sourceAsset: str,
        details: List[Any],
        timestamp: int,
        signature: str,
        requestId: str = None,
        IndexId: int = None,
        subscriptionStartDay: int = None,
        subscriptionStartWeekday: str = None,
        flexibleAllowedToUse: bool = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Investment plan creation (USER_DATA)
        Parameters:
        :param sourceType: No description.
            Type:str
        :param planType: No description.
            Type:str
        :param subscriptionAmount: No description.
            Type:float
        :param subscriptionCycle: No description.
            Type:str
        :param subscriptionStartTime: No description.
            Type:int
        :param sourceAsset: No description.
            Type:str
        :param details: No description.
            Type:List[Any]
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param requestId: No description.
            Type:str
        :param IndexId: No description.
            Type:int
        :param subscriptionStartDay: No description.
            Type:int
        :param subscriptionStartWeekday: No description.
            Type:str
        :param flexibleAllowedToUse: No description.
            Type:bool
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Plan result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/lending/auto-invest/plan/add",
            params={
                "sourceType": sourceType,
                "planType": planType,
                "subscriptionAmount": subscriptionAmount,
                "subscriptionCycle": subscriptionCycle,
                "subscriptionStartTime": subscriptionStartTime,
                "sourceAsset": sourceAsset,
                "details": details,
                "timestamp": timestamp,
                "signature": signature,
                "requestId": requestId,
                "IndexId": IndexId,
                "subscriptionStartDay": subscriptionStartDay,
                "subscriptionStartWeekday": subscriptionStartWeekday,
                "flexibleAllowedToUse": flexibleAllowedToUse,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_lending_auto_invest_plan_edit(
        self,
        planId: int,
        subscriptionAmount: float,
        subscriptionCycle: str,
        subscriptionStartTime: int,
        sourceAsset: str,
        timestamp: int,
        signature: str,
        subscriptionStartDay: int = None,
        subscriptionStartWeekday: str = None,
        flexibleAllowedToUse: bool = None,
        details: List[Any] = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Investment plan adjustment
        Parameters:
        :param planId: No description.
            Type:int
        :param subscriptionAmount: No description.
            Type:float
        :param subscriptionCycle: No description.
            Type:str
        :param subscriptionStartTime: No description.
            Type:int
        :param sourceAsset: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param subscriptionStartDay: No description.
            Type:int
        :param subscriptionStartWeekday: No description.
            Type:str
        :param flexibleAllowedToUse: No description.
            Type:bool
        :param details: No description.
            Type:List[Any]
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Plan result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/lending/auto-invest/plan/edit",
            params={
                "planId": planId,
                "subscriptionAmount": subscriptionAmount,
                "subscriptionCycle": subscriptionCycle,
                "subscriptionStartTime": subscriptionStartTime,
                "sourceAsset": sourceAsset,
                "timestamp": timestamp,
                "signature": signature,
                "subscriptionStartDay": subscriptionStartDay,
                "subscriptionStartWeekday": subscriptionStartWeekday,
                "flexibleAllowedToUse": flexibleAllowedToUse,
                "details": details,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_lending_auto_invest_plan_edit_status(
        self,
        planId: int,
        status: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Change Plan Status
        Parameters:
        :param planId: No description.
            Type:int
        :param status: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Plan result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/lending/auto-invest/plan/edit-status",
            params={
                "planId": planId,
                "status": status,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_lending_auto_invest_plan_list_(
        self,
        planType: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get list of plans
        Parameters:
        :param planType: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Plan result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/lending/auto-invest/plan/list",
            params={
                "planType": planType,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_lending_auto_invest_plan_id_(
        self,
        timestamp: int,
        signature: str,
        planId: int = None,
        requestId: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query holding details of the plan
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param planId: No description.
            Type:int
        :param requestId: No description.
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Plan result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/lending/auto-invest/plan/id",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "planId": planId,
                "requestId": requestId,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_lending_auto_invest_history_list_(
        self,
        timestamp: int,
        signature: str,
        planId: int = None,
        startTime: int = None,
        endTime: int = None,
        targetAsset: float = None,
        planType: str = None,
        size: int = None,
        current: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query subscription transaction history
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param planId: No description.
            Type:int
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param targetAsset: No description.
            Type:float
        :param planType: No description.
            Type:str
        :param size: Default:10 Max:100
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Plan result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/lending/auto-invest/history/list",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "planId": planId,
                "startTime": startTime,
                "endTime": endTime,
                "targetAsset": targetAsset,
                "planType": planType,
                "size": size,
                "current": current,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_lending_auto_invest_index_info(
        self,
        indexId: int,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Index Details(USER_DATA)
        Parameters:
        :param indexId: No description.
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Index result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/lending/auto-invest/index/info",
            params={
                "indexId": indexId,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_lending_auto_invest_index_user_summary(
        self,
        indexId: int,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query Index Linked Plan Position Details(USER_DATA)
        Parameters:
        :param indexId: No description.
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Position Details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/lending/auto-invest/index/user-summary",
            params={
                "indexId": indexId,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_lending_auto_invest_one_off(
        self,
        sourceType: str,
        subscriptionAmount: float,
        sourceAsset: str,
        timestamp: int,
        signature: str,
        requestId: str = None,
        flexibleAllowedToUse: bool = None,
        planId: int = None,
        indexId: int = None,
        details: List[Any] = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        One Time Transaction(TRADE)
        Parameters:
        :param sourceType: No description.
            Type:str
        :param subscriptionAmount: No description.
            Type:float
        :param sourceAsset: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param requestId: No description.
            Type:str
        :param flexibleAllowedToUse: No description.
            Type:bool
        :param planId: No description.
            Type:int
        :param indexId: No description.
            Type:int
        :param details: No description.
            Type:List[Any]
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: transaction result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/lending/auto-invest/one-off",
            params={
                "sourceType": sourceType,
                "subscriptionAmount": subscriptionAmount,
                "sourceAsset": sourceAsset,
                "timestamp": timestamp,
                "signature": signature,
                "requestId": requestId,
                "flexibleAllowedToUse": flexibleAllowedToUse,
                "planId": planId,
                "indexId": indexId,
                "details": details,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_lending_auto_invest_one_off_status(
        self,
        transactionId: int,
        timestamp: int,
        signature: str,
        requestId: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Query One-Time Transaction Status (USER_DATA)
        Parameters:
        :param transactionId: No description.
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param requestId: No description.
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: transaction result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/lending/auto-invest/one-off/status",
            params={
                "transactionId": transactionId,
                "timestamp": timestamp,
                "signature": signature,
                "requestId": requestId,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_lending_auto_invest_redeem(
        self,
        indexId: int,
        redemptionPercentage: int,
        timestamp: int,
        signature: str,
        requestId: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Index Linked Plan Redemption (TRADE)
        Parameters:
        :param indexId: PORTFOLIO plan's Id
            Type:int
        :param redemptionPercentage: user redeem percentage,10/20/100.
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param requestId: sourceType + unique, transactionId and requestId cannot be empty at the same time
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Redemption result
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/lending/auto-invest/redeem",
            params={
                "indexId": indexId,
                "redemptionPercentage": redemptionPercentage,
                "timestamp": timestamp,
                "signature": signature,
                "requestId": requestId,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_lending_auto_invest_redeem_history(
        self,
        requestId: int,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        asset: str = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Index Linked Plan Redemption History (USER_DATA)
        Parameters:
        :param requestId: No description.
            Type:int
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param asset: No description.
            Type:str
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Redemption history
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/lending/auto-invest/redeem/history",
            params={
                "requestId": requestId,
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "asset": asset,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_lending_auto_invest_rebalance_history(
        self,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Index Linked Plan Rebalance Details (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Rebalance Details
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/lending/auto-invest/rebalance/history",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_eth_staking_eth_stake(
        self,
        amount: float,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Subscribe ETH Staking V2(TRADE)
        Parameters:
        :param amount: Amount in ETH, limit 4 decimals
            Type:float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Subscribed WBETH
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v2/eth-staking/eth/stake",
            params={
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_eth_staking_eth_redeem(
        self,
        amount: float,
        timestamp: int,
        signature: str,
        asset: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Redeem ETH (TRADE)
        Parameters:
        :param amount: Amount in BETH, limit 8 decimals
            Type:float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param asset: WBETH or BETH, default to BETH
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Returned ETH
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/eth-staking/eth/redeem",
            params={
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "asset": asset,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_eth_staking_eth_history_staking_history(
        self,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get ETH staking history (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: ETH staking history
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/eth-staking/eth/history/stakingHistory",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_eth_staking_eth_history_redemption_history(
        self,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get ETH redemption history (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: ETH redemption history
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/eth-staking/eth/history/redemptionHistory",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_eth_staking_eth_history_rewards_history(
        self,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get BETH rewards distribution history(USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: BETH rewards distribution history
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/eth-staking/eth/history/rewardsHistory",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_eth_staking_eth_quota(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get current ETH staking quota (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Eth staking quota
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/eth-staking/eth/quota",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_eth_staking_eth_history_rate_history(
        self,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get WBETH Rate History (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: WBETH Rate History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/eth-staking/eth/history/rateHistory",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_eth_staking_account(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        ETH Staking account V2(USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: ETH Staking account
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v2/eth-staking/account",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_eth_staking_wbeth_wrap(
        self,
        amount: float,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Wrap BETH(TRADE)
        Parameters:
        :param amount: Amount in BETH, limit 4 decimals
            Type:float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Wrap BETH
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/eth-staking/wbeth/wrap",
            params={
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_eth_staking_wbeth_history_wrap_history(
        self,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get WBETH wrap history (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: WBETH wrap history
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/eth-staking/wbeth/history/wrapHistory",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_eth_staking_wbeth_history_unwrap_history(
        self,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get WBETH unwrap history (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: WBETH unwrap history
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/eth-staking/wbeth/history/unwrapHistory",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_eth_staking_eth_history_wbeth_rewards_history(
        self,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get WBETH rewards history(USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: WBETH rewards history
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/eth-staking/eth/history/wbethRewardsHistory",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_copy_trading_futures_user_status(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Futures Lead Trader Status(TRADE)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Futures Lead Trader Status
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/copyTrading/futures/userStatus",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_copy_trading_futures_lead_symbol(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Futures Lead Trading Symbol Whitelist(USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Futures Lead Trading Symbol Whitelist
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/copyTrading/futures/leadSymbol",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_flexible_list_(
        self,
        timestamp: int,
        signature: str,
        asset: str = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Simple Earn Flexible Product List (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param asset: No description.
            Type:str
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Simple Earn Flexible Product List
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/flexible/list",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "asset": asset,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_locked_list_(
        self,
        timestamp: int,
        signature: str,
        asset: str = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Simple Earn Locked Product List (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param asset: No description.
            Type:str
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Simple Earn Locked Product List
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/locked/list",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "asset": asset,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_simple_earn_flexible_subscribe(
        self,
        productId: str,
        amount: float,
        timestamp: int,
        signature: str,
        autoSubscribe: bool = None,
        sourceAccount: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Subscribe Flexible Product (TRADE)
        Parameters:
        :param productId: No description.
            Type:str
        :param amount: No description.
            Type:float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param autoSubscribe: true or false, default true.
            Type:bool
        :param sourceAccount: SPOT,FUND,ALL, default SPOT
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Flexible Product Subscription Response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/simple-earn/flexible/subscribe",
            params={
                "productId": productId,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "autoSubscribe": autoSubscribe,
                "sourceAccount": sourceAccount,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_simple_earn_locked_subscribe(
        self,
        projectId: str,
        amount: float,
        timestamp: int,
        signature: str,
        autoSubscribe: bool = None,
        sourceAccount: str = None,
        redeemTo: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Subscribe Locked Product (TRADE)
        Parameters:
        :param projectId: No description.
            Type:str
        :param amount: No description.
            Type:float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param autoSubscribe: true or false, default true.
            Type:bool
        :param sourceAccount: SPOT,FUND,ALL, default SPOT
            Type:str
        :param redeemTo: SPOT,FLEXIBLE, default FLEXIBLE
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Locked Product Subscription Response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/simple-earn/locked/subscribe",
            params={
                "projectId": projectId,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "autoSubscribe": autoSubscribe,
                "sourceAccount": sourceAccount,
                "redeemTo": redeemTo,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_simple_earn_flexible_redeem(
        self,
        productId: str,
        timestamp: int,
        signature: str,
        redeemAll: bool = None,
        amount: float = None,
        destAccount: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Redeem Flexible Product (TRADE)
        Parameters:
        :param productId: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param redeemAll: true or false, default to false
            Type:bool
        :param amount: if redeemAll is false, amount is mandatory
            Type:float
        :param destAccount: SPOT,FUND,ALL, default SPOT
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Redeem Flexible Product
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/simple-earn/flexible/redeem",
            params={
                "productId": productId,
                "timestamp": timestamp,
                "signature": signature,
                "redeemAll": redeemAll,
                "amount": amount,
                "destAccount": destAccount,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_simple_earn_locked_redeem(
        self,
        positionId: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Redeem Locked Product (TRADE)
        Parameters:
        :param positionId: 1234
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Redeem Locked Product
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/simple-earn/locked/redeem",
            params={
                "positionId": positionId,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_flexible_position(
        self,
        timestamp: int,
        signature: str,
        asset: str = None,
        productId: str = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Flexible Product Position (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param asset: No description.
            Type:str
        :param productId: No description.
            Type:str
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Flexible Product Position
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/flexible/position",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "asset": asset,
                "productId": productId,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_locked_position(
        self,
        timestamp: int,
        signature: str,
        asset: str = None,
        positionId: str = None,
        projectId: str = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Locked Product Position (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param asset: No description.
            Type:str
        :param positionId: No description.
            Type:str
        :param projectId: No description.
            Type:str
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Locked Product Position
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/locked/position",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "asset": asset,
                "positionId": positionId,
                "projectId": projectId,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_account(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Simple Account (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Account Information
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/account",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_flexible_history_subscription_record(
        self,
        timestamp: int,
        signature: str,
        productId: str = None,
        purchaseId: str = None,
        asset: str = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Flexible Subscription Record (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param productId: No description.
            Type:str
        :param purchaseId: No description.
            Type:str
        :param asset: No description.
            Type:str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Flexible Product Position
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/flexible/history/subscriptionRecord",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "productId": productId,
                "purchaseId": purchaseId,
                "asset": asset,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_locked_history_subscription_record(
        self,
        timestamp: int,
        signature: str,
        purchaseId: str = None,
        asset: str = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Locked Subscription Record (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param purchaseId: No description.
            Type:str
        :param asset: No description.
            Type:str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Locked Subscription Record
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/locked/history/subscriptionRecord",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "purchaseId": purchaseId,
                "asset": asset,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_flexible_history_redemption_record(
        self,
        productId: str = None,
        redeemId: str = None,
        asset: str = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
    ) -> Dict[str, Any]:
        """
        Get Flexible Redemption Record (USER_DATA)
        Parameters:
        :param productId: No description.
            Type:str
        :param redeemId: No description.
            Type:str
        :param asset: No description.
            Type:str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int.
        :returns: Flexible Redemption Record
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/flexible/history/redemptionRecord",
            params={
                "productId": productId,
                "redeemId": redeemId,
                "asset": asset,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
            },
        )

    def get_sapi_simple_earn_locked_history_redemption_record(
        self,
        timestamp: int,
        signature: str,
        positionId: str = None,
        redeemId: str = None,
        asset: str = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Locked Redemption Record (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param positionId: No description.
            Type:str
        :param redeemId: No description.
            Type:str
        :param asset: No description.
            Type:str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Locked Redemption Record
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/locked/history/redemptionRecord",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "positionId": positionId,
                "redeemId": redeemId,
                "asset": asset,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_flexible_history_rewards_record(
        self,
        type_: str,
        productId: str = None,
        asset: str = None,
        startTime: int = None,
        endTime: int = None,
    ) -> Dict[str, Any]:
        """
        Get Flexible Rewards History (USER_DATA)
        Parameters:
        :param type_: "BONUS", "REALTIME", "REWARDS"
            Type:str
        :param productId: No description.
            Type:str
        :param asset: No description.
            Type:str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int.
        :returns: Flexible Rewards History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/flexible/history/rewardsRecord",
            params={
                "type": type_,
                "productId": productId,
                "asset": asset,
                "startTime": startTime,
                "endTime": endTime,
            },
        )

    def get_sapi_simple_earn_locked_history_rewards_record(
        self,
        timestamp: int,
        signature: str,
        positionId: str = None,
        asset: str = None,
        startTime: int = None,
        endTime: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Locked Rewards History (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param positionId: No description.
            Type:str
        :param asset: No description.
            Type:str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Locked Rewards History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/locked/history/rewardsRecord",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "positionId": positionId,
                "asset": asset,
                "startTime": startTime,
                "endTime": endTime,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_simple_earn_flexible_set_auto_subscribe(
        self,
        productId: str,
        autoSubscribe: bool,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Set Flexible Auto Subscribe (USER_DATA)
        Parameters:
        :param productId: No description.
            Type:str
        :param autoSubscribe: true or false
            Type:bool
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Flexible Product Subscription Response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/simple-earn/flexible/setAutoSubscribe",
            params={
                "productId": productId,
                "autoSubscribe": autoSubscribe,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_simple_earn_locked_set_auto_subscribe(
        self,
        positionId: str,
        autoSubscribe: bool,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Set Locked Auto Subscribe (USER_DATA)
        Parameters:
        :param positionId: No description.
            Type:str
        :param autoSubscribe: true or false
            Type:bool
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Locked Auto Subscribe
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/simple-earn/locked/setAutoSubscribe",
            params={
                "positionId": positionId,
                "autoSubscribe": autoSubscribe,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_flexible_personal_left_quota(
        self,
        productId: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Flexible Personal Left Quota (USER_DATA)
        Parameters:
        :param productId: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Flexible Personal Left Quota
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/flexible/personalLeftQuota",
            params={
                "productId": productId,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_locked_personal_left_quota(
        self,
        projectId: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Locked Personal Left Quota (USER_DATA)
        Parameters:
        :param projectId: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Locked Personal Left Quota
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/locked/personalLeftQuota",
            params={
                "projectId": projectId,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_flexible_subscription_preview(
        self,
        productId: str,
        amount: float,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Flexible Subscription Preview (USER_DATA)
        Parameters:
        :param productId: No description.
            Type:str
        :param amount: No description.
            Type:float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Flexible Subscription Preview
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/flexible/subscriptionPreview",
            params={
                "productId": productId,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_locked_subscription_preview(
        self,
        projectId: str,
        amount: float,
        timestamp: int,
        signature: str,
        autoSubscribe: bool = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Locked Subscription Preview (USER_DATA)
        Parameters:
        :param projectId: No description.
            Type:str
        :param amount: No description.
            Type:float
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param autoSubscribe: true or false, default true.
            Type:bool
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Locked Product Subscription Response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/locked/subscriptionPreview",
            params={
                "projectId": projectId,
                "amount": amount,
                "timestamp": timestamp,
                "signature": signature,
                "autoSubscribe": autoSubscribe,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_locked_set_redeem_option(
        self,
        positionId: str,
        timestamp: int,
        signature: str,
        redeemTo: str = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Set Locked Product Redeem Option(USER_DATA)
        Parameters:
        :param positionId: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param redeemTo: SPOT,FLEXIBLE, default FLEXIBLE
            Type:str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Locked Product Redeem Option
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/locked/setRedeemOption",
            params={
                "positionId": positionId,
                "timestamp": timestamp,
                "signature": signature,
                "redeemTo": redeemTo,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_flexible_history_rate_history(
        self,
        productId: str,
        timestamp: int,
        signature: str,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Rate History (USER_DATA)
        Parameters:
        :param productId: No description.
            Type:str
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Rate History
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/flexible/history/rateHistory",
            params={
                "productId": productId,
                "timestamp": timestamp,
                "signature": signature,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_simple_earn_flexible_history_collateral_record(
        self,
        timestamp: int,
        signature: str,
        productId: str = None,
        startTime: int = None,
        endTime: int = None,
        current: int = None,
        size: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Get Collateral Record (USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param productId: No description.
            Type:str
        :param startTime: UTC timestamp in ms
            Type: int
        :param endTime: UTC timestamp in ms
            Type: int
        :param current: Current querying page. Start from 1. Default:1
            Type: int
        :param size: Default:10 Max:100
            Type: int
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Collateral Record
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/simple-earn/flexible/history/collateralRecord",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "productId": productId,
                "startTime": startTime,
                "endTime": endTime,
                "current": current,
                "size": size,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_dci_product_list_(
        self,
        optionType: str,
        exercisedCoin: str,
        investCoin: str,
        timestamp: int,
        signature: str,
        smallPageSize: str = None,
        pageIndex: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Get Dual Investment product list(USER_DATA)
                Parameters:
                :param optionType: Input CALL or PUT
                    Type:str
                :param exercisedCoin: Target exercised asset, e.g.:
        if you subscribe to a high sell product (call option), you should input:
          - optionType: CALL,
          - exercisedCoin: USDT,
          - investCoin: BNB;

        if you subscribe to a low buy product (put option), you should input:
          - optionType: PUT,
          - exercisedCoin: BNB,
          - investCoin: USDT;
                    Type:str
                :param investCoin: Asset used for subscribing, e.g.:
        if you subscribe to a high sell product (call option), you should input:
          - optionType: CALL,
          - exercisedCoin: USDT,
          - investCoin: BNB;

        if you subscribe to a low buy product (put option), you should input:
          - optionType: PUT,
          - exercisedCoin: BNB,
          - investCoin: USDT;
                    Type:str
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param smallPageSize: MIN 1, MAX 100; Default 100
                    Type: str
                :param pageIndex: Page number, default is first page, start form 1
                    Type: int
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Dual Investment product list
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/dci/product/list",
            params={
                "optionType": optionType,
                "exercisedCoin": exercisedCoin,
                "investCoin": investCoin,
                "timestamp": timestamp,
                "signature": signature,
                "smallPageSize": smallPageSize,
                "pageIndex": pageIndex,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_dci_product_subscribe(
        self,
        id_: str,
        orderId: str,
        depositAmount: float,
        autoCompoundPlan: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Subscribe Dual Investment products(USER_DATA)
                Parameters:
                :param id_: get id from /sapi/v1/dci/product/list
                    Type:str
                :param orderId: get orderId from /sapi/v1/dci/product/list
                    Type:str
                :param depositAmount: No description.
                    Type:float
                :param autoCompoundPlan: NONE: switch off the plan,
        STANDARD: standard plan,
        ADVANCED: advanced plan;
                    Type: str
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Dual Investment product subscription response
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/dci/product/subscribe",
            params={
                "id": id_,
                "orderId": orderId,
                "depositAmount": depositAmount,
                "autoCompoundPlan": autoCompoundPlan,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_dci_product_positions(
        self,
        timestamp: int,
        signature: str,
        status: str = None,
        smallPageSize: str = None,
        pageIndex: int = None,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Get Dual Investment positions(USER_DATA)
                Parameters:
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param status: - PENDING: Products are purchasing, will give results later;
        - PURCHASE_SUCCESS: purchase successfully;
        - SETTLED: Products are finish settling;
        - PURCHASE_FAIL: fail to purchase;
        - REFUNDING: refund ongoing;
        - REFUND_SUCCESS: refund to spot account successfully;
        - SETTLING: Products are settling.
        If don't fill this field, will response all the position status.
                    Type:str
                :param smallPageSize: MIN 1, MAX 100; Default 100
                    Type: str
                :param pageIndex: Page number, default is first page, start form 1
                    Type: int
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Dual Investment product list
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/dci/product/positions",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "status": status,
                "smallPageSize": smallPageSize,
                "pageIndex": pageIndex,
                "recvWindow": recvWindow,
            },
        )

    def get_sapi_dci_product_accounts(
        self,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
        Check Dual Investment accounts(USER_DATA)
        Parameters:
        :param timestamp: UTC timestamp in ms
            Type: int
        :param signature: Signature
            Type: str
        :param recvWindow: The value cannot be greater than 60000
            Type: int.
        :returns: Dual Investment accounts
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/sapi/v1/dci/product/accounts",
            params={
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )

    def post_sapi_dci_product_auto_compound_edit_status(
        self,
        positionId: int,
        autoCompoundPlan: str,
        timestamp: int,
        signature: str,
        recvWindow: int = None,
    ) -> Dict[str, Any]:
        """
                Change Auto-Compound status(USER_DATA)
                Parameters:
                :param positionId: Get positionId from /sapi/v1/dci/product/positions
                    Type:int
                :param autoCompoundPlan: NONE: switch off the plan,
        STANDARD: standard plan,
        ADVANCED: advanced plan;
                    Type: str
                :param timestamp: UTC timestamp in ms
                    Type: int
                :param signature: Signature
                    Type: str
                :param recvWindow: The value cannot be greater than 60000
                    Type: int.
                :returns: Change Auto-Compound status response
                :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/sapi/v1/dci/product/auto_compound/edit-status",
            params={
                "positionId": positionId,
                "autoCompoundPlan": autoCompoundPlan,
                "timestamp": timestamp,
                "signature": signature,
                "recvWindow": recvWindow,
            },
        )
