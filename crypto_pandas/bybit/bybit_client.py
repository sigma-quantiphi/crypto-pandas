from typing import Optional, Dict, Any

import pandas as pd
import requests
from pydantic import BaseModel, Field

from crypto_pandas.binance.binance_requests import prepare_requests_parameters
from crypto_pandas.bybit.authentication import auth
from crypto_pandas.bybit.bybit_pandas import (
    market_kline_response_to_dataframe,
    market_mark_price_kline_response_to_dataframe,
    account_wallet_balance_response_to_dataframe,
)


class BybitClient(BaseModel):
    """
    A client for interacting with the Bybit API.

    :param env: The API env (`prod` or `paper`).
    :param api_key: The API Key for authentication.
    """

    env: str = Field(default="paper", description="The API env (`prod` or `paper`)")
    api_key: str = Field(
        default=None, description="apiKey for OAuth2 authentication", repr=False
    )
    secret: str = Field(
        default=None, description="Secret for OAuth2 authentication", repr=False
    )

    @property
    def base_url(self) -> str:
        return (
            "https://api.bybit.com"
            if self.env == "prod"
            else "https://api-testnet.bybit.com"
        )

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Internal method to make API requests.

        :param method: HTTP method (e.g., GET, POST, PUT, DELETE).
        :param path: Path of the API endpoint.
        :param params: Query parameters for the request.
        :param body: Request body for POST/PUT methods.
        :return: The JSON response from the API.
        """
        request_args = {
            "method": method,
            "url": f"{self.base_url}{path}",
        }
        if params is not None:
            request_args["params"] = prepare_requests_parameters(params)
        if body is not None:
            request_args["json"] = body
        if self.api_key and self.secret:
            request_args["headers"] = auth(
                api_key=self.api_key,
                api_secret=self.secret,
                params=request_args["params"],
            )
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

    @property
    def info(self) -> Dict[str, str]:
        """
        Return API information.

        :returns: A dictionary containing the API title, description, and version.
        """
        return {
            "title": "Open API V5 english",
            "description": """No description provided.""",
            "version": "1.0.0",
        }

    def get_market_kline(
        self,
        symbol: str = None,
        interval: int = None,
        start: pd.Timestamp = None,
        end: pd.Timestamp = None,
        limit: int = None,
        category: str = None,
    ) -> pd.DataFrame:
        """
        kline
        Parameters:
        :param symbol: No description.
            Type:str
        :param interval: No description.
            Type:int
        :param start: No description.
            Type:pd.Timestamp
        :param end: No description.
            Type:pd.Timestamp
        :param limit: No description.
            Type:int
        :param category: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            method="GET",
            path="/v5/market/kline",
            params={
                "symbol": symbol,
                "interval": interval,
                "start": start,
                "end": end,
                "limit": limit,
                "category": category,
            },
        )
        return market_kline_response_to_dataframe(data)

    def get_announcements_index(
        self,
        start: pd.Timestamp = None,
        end: pd.Timestamp = None,
        locale: str = None,
        limit: int = None,
        offset: int = None,
        page: int = None,
    ) -> Dict[str, Any]:
        """
        annoucement
        Parameters:
        :param start: No description.
            Type:pd.Timestamp
        :param end: No description.
            Type:pd.Timestamp
        :param locale: No description.
            Type:str
        :param limit: No description.
            Type:int
        :param offset: No description.
            Type:int
        :param page: No description.
            Type:int.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/announcements/index",
            params={
                "start": start,
                "end": end,
                "locale": locale,
                "limit": limit,
                "offset": offset,
                "page": page,
            },
        )

    def get_market_mark_price_kline(
        self,
        category: str = None,
        symbol: str = None,
        interval: int = None,
        start: pd.Timestamp = None,
        end: pd.Timestamp = None,
        limit: int = None,
    ) -> pd.DataFrame:
        """
        mark-price-kline
        Parameters:
        :param category: No description.
            Type:str
        :param symbol: No description.
            Type:str
        :param interval: No description.
            Type:int
        :param start: No description.
            Type:pd.Timestamp
        :param end: No description.
            Type:pd.Timestamp
        :param limit: No description.
            Type:int.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            method="GET",
            path="/v5/market/mark-price-kline",
            params={
                "category": category,
                "symbol": symbol,
                "interval": interval,
                "start": start,
                "end": end,
                "limit": limit,
            },
        )
        return market_mark_price_kline_response_to_dataframe(data)

    def get_market_index_price_kline(
        self,
        category: str = None,
        symbol: str = None,
        interval: int = None,
        start: pd.Timestamp = None,
        end: pd.Timestamp = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """
        index-price-kline
        Parameters:
        :param category: No description.
            Type:str
        :param symbol: No description.
            Type:str
        :param interval: No description.
            Type:int
        :param start: No description.
            Type:pd.Timestamp
        :param end: No description.
            Type:pd.Timestamp
        :param limit: No description.
            Type:int.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/market/index-price-kline",
            params={
                "category": category,
                "symbol": symbol,
                "interval": interval,
                "start": start,
                "end": end,
                "limit": limit,
            },
        )

    def get_market_premium_index_price_kline(
        self,
        category: str = None,
        symbol: str = None,
        interval: int = None,
        start: pd.Timestamp = None,
        end: pd.Timestamp = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """
        premium-index-price-kline
        Parameters:
        :param category: No description.
            Type:str
        :param symbol: No description.
            Type:str
        :param interval: No description.
            Type:int
        :param start: No description.
            Type:pd.Timestamp
        :param end: No description.
            Type:pd.Timestamp
        :param limit: No description.
            Type:int.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/market/premium-index-price-kline",
            params={
                "category": category,
                "symbol": symbol,
                "interval": interval,
                "start": start,
                "end": end,
                "limit": limit,
            },
        )

    def get_market_orderbook(
        self,
        category: str = None,
        symbol: str = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """
        orderbook
        Parameters:
        :param category: linear inverse
            Type:str
        :param symbol: No description.
            Type:str
        :param limit: No description.
            Type:int.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/market/orderbook",
            params={
                "category": category,
                "symbol": symbol,
                "limit": limit,
            },
        )

    def get_market_instruments_info(
        self,
        category: str = None,
        symbol: str = None,
        limit: int = None,
        cursor: str = None,
        baseCoin: str = None,
        direction: str = None,
    ) -> Dict[str, Any]:
        """
        instruments-info
        Parameters:
        :param category: No description.
            Type:str
        :param symbol: BTCUSDH23
            Type:str
        :param limit: No description.
            Type:int
        :param cursor: No description.
            Type:str
        :param baseCoin: No description.
            Type:str
        :param direction: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/market/instruments-info",
            params={
                "category": category,
                "symbol": symbol,
                "limit": limit,
                "cursor": cursor,
                "baseCoin": baseCoin,
                "direction": direction,
            },
        )

    def get_market_tickers(
        self,
        category: str = None,
        symbol: str = None,
        limit: int = None,
        baseCoin: str = None,
    ) -> Dict[str, Any]:
        """
        tickers
        Parameters:
        :param category: linear inverse option
            Type:str
        :param symbol: BTCPERP
            Type:str
        :param limit: No description.
            Type:int
        :param baseCoin: No description.
            Type:str.
        :returns: OK
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/market/tickers",
            params={
                "category": category,
                "symbol": symbol,
                "limit": limit,
                "baseCoin": baseCoin,
            },
        )

    def get_market_funding_history(
        self,
        category: str = None,
        symbol: str = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """
        funding/history
        Parameters:
        :param category: No description.
            Type:str
        :param symbol: No description.
            Type:str
        :param limit: No description.
            Type:int.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/market/funding/history",
            params={
                "category": category,
                "symbol": symbol,
                "limit": limit,
            },
        )

    def get_market_risk_limit(
        self,
        category: str = None,
        symbol: str = None,
        interval: int = None,
        start: pd.Timestamp = None,
        end: pd.Timestamp = None,
        limit: int = None,
    ) -> Dict[str, Any]:
        """
        risk-limit
        Parameters:
        :param category: No description.
            Type:str
        :param symbol: BTCPERP
            Type:str
        :param interval: No description.
            Type:int
        :param start: No description.
            Type:pd.Timestamp
        :param end: No description.
            Type:pd.Timestamp
        :param limit: No description.
            Type:int.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/market/risk-limit",
            params={
                "category": category,
                "symbol": symbol,
                "interval": interval,
                "start": start,
                "end": end,
                "limit": limit,
            },
        )

    def get_market_open_interest(
        self,
        category: str = None,
        symbol: str = None,
        intervalTime: str = None,
        startTime: int = None,
        endTime: int = None,
        limit: int = None,
        cursor: str = None,
    ) -> Dict[str, Any]:
        """
        open-interest
        Parameters:
        :param category: linear
            Type:str
        :param symbol: No description.
            Type:str
        :param intervalTime: No description.
            Type:str
        :param startTime: No description.
            Type:int
        :param endTime: No description.
            Type:int
        :param limit: No description.
            Type:int
        :param cursor: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/market/open-interest",
            params={
                "category": category,
                "symbol": symbol,
                "intervalTime": intervalTime,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "cursor": cursor,
            },
        )

    def get_market_insurance(
        self,
        coin: str = None,
    ) -> Dict[str, Any]:
        """
        insurance
        Parameters:
        :param coin: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/market/insurance",
            params={
                "coin": coin,
            },
        )

    def get_market_recent_trade(
        self,
        category: str = None,
        symbol: str = None,
        interval: int = None,
        start: pd.Timestamp = None,
        end: pd.Timestamp = None,
    ) -> Dict[str, Any]:
        """
        recent-trade
        Parameters:
        :param category: linear
            Type:str
        :param symbol: No description.
            Type:str
        :param interval: No description.
            Type:int
        :param start: No description.
            Type:pd.Timestamp
        :param end: No description.
            Type:pd.Timestamp.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/market/recent-trade",
            params={
                "category": category,
                "symbol": symbol,
                "interval": interval,
                "start": start,
                "end": end,
            },
        )

    def get_market_delivery_price(
        self,
        category: str = None,
        baseCoin: str = None,
        period: str = None,
        symbol: str = None,
        limit: int = None,
        cursor: str = None,
        direction: str = None,
    ) -> Dict[str, Any]:
        """
        delivery-price
        Parameters:
        :param category: No description.
            Type:str
        :param baseCoin: No description.
            Type:str
        :param period: No description.
            Type:str
        :param symbol: No description.
            Type:str
        :param limit: No description.
            Type:int
        :param cursor: No description.
            Type:str
        :param direction: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/market/delivery-price",
            params={
                "category": category,
                "baseCoin": baseCoin,
                "period": period,
                "symbol": symbol,
                "limit": limit,
                "cursor": cursor,
                "direction": direction,
            },
        )

    def get_market_historical_volatility(
        self,
        category: str = None,
        baseCoin: str = None,
        period: int = None,
    ) -> Dict[str, Any]:
        """
        historical-volatility
        Parameters:
        :param category: No description.
            Type:str
        :param baseCoin: No description.
            Type:str
        :param period: No description.
            Type:int.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/market/historical-volatility",
            params={
                "category": category,
                "baseCoin": baseCoin,
                "period": period,
            },
        )

    def post_order_create(
        self,
        symbol: str = None,
        orderType: str = None,
        side: str = None,
        qty: float = None,
        timeInForce: str = None,
        positionIdx: str = None,
        orderLinkId: str = None,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        create（Conditional Order）
        Parameters:
        :param symbol: No description.
            Type:str
        :param orderType: No description.
            Type:str
        :param side: No description.
            Type:str
        :param qty: No description.
            Type:float
        :param timeInForce: No description.
            Type:str
        :param positionIdx: No description.
            Type:str
        :param orderLinkId: No description.
            Type:str
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/v5/order/create",
            params={
                "symbol": symbol,
                "orderType": orderType,
                "side": side,
                "qty": qty,
                "timeInForce": timeInForce,
                "positionIdx": positionIdx,
                "orderLinkId": orderLinkId,
            },
            body=body,
        )

    def post_order_create_batch(
        self,
        symbol: str = None,
        orderType: str = None,
        side: str = None,
        qty: float = None,
        timeInForce: str = None,
        positionIdx: str = None,
        orderLinkId: str = None,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        create-batch
        Parameters:
        :param symbol: No description.
            Type:str
        :param orderType: No description.
            Type:str
        :param side: No description.
            Type:str
        :param qty: No description.
            Type:float
        :param timeInForce: No description.
            Type:str
        :param positionIdx: No description.
            Type:str
        :param orderLinkId: No description.
            Type:str
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/v5/order/create-batch",
            params={
                "symbol": symbol,
                "orderType": orderType,
                "side": side,
                "qty": qty,
                "timeInForce": timeInForce,
                "positionIdx": positionIdx,
                "orderLinkId": orderLinkId,
            },
            body=body,
        )

    def post_order_amend_batch(
        self,
        symbol: str = None,
        orderType: str = None,
        side: str = None,
        qty: float = None,
        timeInForce: str = None,
        positionIdx: str = None,
        orderLinkId: str = None,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        amend-batch
        Parameters:
        :param symbol: No description.
            Type:str
        :param orderType: No description.
            Type:str
        :param side: No description.
            Type:str
        :param qty: No description.
            Type:float
        :param timeInForce: No description.
            Type:str
        :param positionIdx: No description.
            Type:str
        :param orderLinkId: No description.
            Type:str
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/v5/order/amend-batch",
            params={
                "symbol": symbol,
                "orderType": orderType,
                "side": side,
                "qty": qty,
                "timeInForce": timeInForce,
                "positionIdx": positionIdx,
                "orderLinkId": orderLinkId,
            },
            body=body,
        )

    def post_order_cancel_batch(
        self,
        symbol: str = None,
        orderType: str = None,
        side: str = None,
        qty: float = None,
        timeInForce: str = None,
        positionIdx: str = None,
        orderLinkId: str = None,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        cancel-batch
        Parameters:
        :param symbol: No description.
            Type:str
        :param orderType: No description.
            Type:str
        :param side: No description.
            Type:str
        :param qty: No description.
            Type:float
        :param timeInForce: No description.
            Type:str
        :param positionIdx: No description.
            Type:str
        :param orderLinkId: No description.
            Type:str
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/v5/order/cancel-batch",
            params={
                "symbol": symbol,
                "orderType": orderType,
                "side": side,
                "qty": qty,
                "timeInForce": timeInForce,
                "positionIdx": positionIdx,
                "orderLinkId": orderLinkId,
            },
            body=body,
        )

    def post_order_amend(
        self,
        symbol: str = None,
        orderType: str = None,
        side: str = None,
        qty: float = None,
        timeInForce: str = None,
        positionIdx: str = None,
        orderLinkId: str = None,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        amend
        Parameters:
        :param symbol: No description.
            Type:str
        :param orderType: No description.
            Type:str
        :param side: No description.
            Type:str
        :param qty: No description.
            Type:float
        :param timeInForce: No description.
            Type:str
        :param positionIdx: No description.
            Type:str
        :param orderLinkId: No description.
            Type:str
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/v5/order/amend",
            params={
                "symbol": symbol,
                "orderType": orderType,
                "side": side,
                "qty": qty,
                "timeInForce": timeInForce,
                "positionIdx": positionIdx,
                "orderLinkId": orderLinkId,
            },
            body=body,
        )

    def post_order_cancel(
        self,
        symbol: str = None,
        orderType: str = None,
        side: str = None,
        qty: float = None,
        timeInForce: str = None,
        positionIdx: str = None,
        orderLinkId: str = None,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        cancel
        Parameters:
        :param symbol: No description.
            Type:str
        :param orderType: No description.
            Type:str
        :param side: No description.
            Type:str
        :param qty: No description.
            Type:float
        :param timeInForce: No description.
            Type:str
        :param positionIdx: No description.
            Type:str
        :param orderLinkId: No description.
            Type:str
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/v5/order/cancel",
            params={
                "symbol": symbol,
                "orderType": orderType,
                "side": side,
                "qty": qty,
                "timeInForce": timeInForce,
                "positionIdx": positionIdx,
                "orderLinkId": orderLinkId,
            },
            body=body,
        )

    def post_order_cancel_all(
        self,
        symbol: str = None,
        orderType: str = None,
        side: str = None,
        qty: float = None,
        timeInForce: str = None,
        positionIdx: str = None,
        orderLinkId: str = None,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        cancel-all
        Parameters:
        :param symbol: No description.
            Type:str
        :param orderType: No description.
            Type:str
        :param side: No description.
            Type:str
        :param qty: No description.
            Type:float
        :param timeInForce: No description.
            Type:str
        :param positionIdx: No description.
            Type:str
        :param orderLinkId: No description.
            Type:str
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/v5/order/cancel-all",
            params={
                "symbol": symbol,
                "orderType": orderType,
                "side": side,
                "qty": qty,
                "timeInForce": timeInForce,
                "positionIdx": positionIdx,
                "orderLinkId": orderLinkId,
            },
            body=body,
        )

    def get_order_realtime(
        self,
        baseCoin: str = None,
        settleCoin: str = None,
        openOnly: int = None,
        orderFilter: str = None,
        cursor: str = None,
        limit: int = None,
        orderId: int = None,
        category: str = None,
        orderStatus: str = None,
        symbol: str = None,
    ) -> Dict[str, Any]:
        """
        order/realtime
        Parameters:
        :param baseCoin: No description.
            Type:str
        :param settleCoin: No description.
            Type:str
        :param openOnly: No description.
            Type:int
        :param orderFilter: No description.
            Type:str
        :param cursor: No description.
            Type:str
        :param limit: No description.
            Type:int
        :param orderId: No description.
            Type:int
        :param category: No description.
            Type:str
        :param orderStatus: No description.
            Type:str
        :param symbol: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/order/realtime",
            params={
                "baseCoin": baseCoin,
                "settleCoin": settleCoin,
                "openOnly": openOnly,
                "orderFilter": orderFilter,
                "cursor": cursor,
                "limit": limit,
                "orderId": orderId,
                "category": category,
                "orderStatus": orderStatus,
                "symbol": symbol,
            },
        )

    def get_order_history(
        self,
        category: str = None,
        orderType: str = None,
        side: str = None,
        cursor: str = None,
        orderFilter: str = None,
        limit: int = None,
        orderStatus: str = None,
        symbol: str = None,
        baseCoin: str = None,
        orderId: int = None,
    ) -> Dict[str, Any]:
        """
        order/history
        Parameters:
        :param category: No description.
            Type:str
        :param orderType: No description.
            Type:str
        :param side: No description.
            Type:str
        :param cursor: No description.
            Type:str
        :param orderFilter: No description.
            Type:str
        :param limit: No description.
            Type:int
        :param orderStatus: No description.
            Type:str
        :param symbol: No description.
            Type:str
        :param baseCoin: No description.
            Type:str
        :param orderId: No description.
            Type:int.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/order/history",
            params={
                "category": category,
                "orderType": orderType,
                "side": side,
                "cursor": cursor,
                "orderFilter": orderFilter,
                "limit": limit,
                "orderStatus": orderStatus,
                "symbol": symbol,
                "baseCoin": baseCoin,
                "orderId": orderId,
            },
        )

    def get_order_spot_borrow_check(
        self,
        category: str = None,
        symbol: str = None,
        side: str = None,
    ) -> Dict[str, Any]:
        """
        spot borrow check
        Parameters:
        :param category: No description.
            Type:str
        :param symbol: No description.
            Type:str
        :param side: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/order/spot-borrow-check",
            params={
                "category": category,
                "symbol": symbol,
                "side": side,
            },
        )

    def get_execution_list_(
        self,
        category: str = None,
        startTime: int = None,
        symbol: str = None,
        endTime: int = None,
        cursor: str = None,
        orderLinkId: str = None,
        execType: str = None,
    ) -> Dict[str, Any]:
        """
        execution/list
        Parameters:
        :param category: No description.
            Type:str
        :param startTime: No description.
            Type:int
        :param symbol: No description.
            Type:str
        :param endTime: No description.
            Type:int
        :param cursor: No description.
            Type:str
        :param orderLinkId: No description.
            Type:str
        :param execType: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/execution/list",
            params={
                "category": category,
                "startTime": startTime,
                "symbol": symbol,
                "endTime": endTime,
                "cursor": cursor,
                "orderLinkId": orderLinkId,
                "execType": execType,
            },
        )

    def get_position_list_(
        self,
        cursor: str = None,
        settleCoin: str = None,
        symbol: str = None,
        category: str = None,
    ) -> Dict[str, Any]:
        """
        position/list
        Parameters:
        :param cursor: No description.
            Type:str
        :param settleCoin: No description.
            Type:str
        :param symbol: No description.
            Type:str
        :param category: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/position/list",
            params={
                "cursor": cursor,
                "settleCoin": settleCoin,
                "symbol": symbol,
                "category": category,
            },
        )

    def post_position_switch_isolated(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        switch-isolated
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/position/switch-isolated", params={}, body=body
        )

    def post_position_switch_mode(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        switch-mode
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/position/switch-mode", params={}, body=body
        )

    def post_position_set_tpsl_mode(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        set-tpsl-mode
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/position/set-tpsl-mode", params={}, body=body
        )

    def post_position_trading_stop(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        trading-stop
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/position/trading-stop", params={}, body=body
        )

    def post_position_set_leverage(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        set-leverage
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/position/set-leverage", params={}, body=body
        )

    def post_position_set_risk_limit(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        set-risk-limit
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/position/set-risk-limit", params={}, body=body
        )

    def post_position_set_auto_add_margin(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        set-auto-add-margin
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/v5/position/set-auto-add-margin",
            params={},
            body=body,
        )

    def get_position_closed_pnl(
        self,
        category: str = None,
        startTime: str = None,
        symbol: str = None,
        limit: int = None,
        cursor: str = None,
        endTime: int = None,
    ) -> Dict[str, Any]:
        """
        closed-pnl
        Parameters:
        :param category: No description.
            Type:str
        :param startTime: No description.
            Type:str
        :param symbol: LINKUSDT
            Type:str
        :param limit: No description.
            Type:int
        :param cursor: No description.
            Type:str
        :param endTime: No description.
            Type:int.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/position/closed-pnl",
            params={
                "category": category,
                "startTime": startTime,
                "symbol": symbol,
                "limit": limit,
                "cursor": cursor,
                "endTime": endTime,
            },
        )

    def get_asset_delivery_record(
        self,
        category: str = None,
        startTime: str = None,
        symbol: str = None,
        limit: int = None,
        cursor: str = None,
        endTime: int = None,
    ) -> Dict[str, Any]:
        """
        delivery-record
        Parameters:
        :param category: No description.
            Type:str
        :param startTime: No description.
            Type:str
        :param symbol: LINKUSDT
            Type:str
        :param limit: No description.
            Type:int
        :param cursor: No description.
            Type:str
        :param endTime: No description.
            Type:int.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/delivery-record",
            params={
                "category": category,
                "startTime": startTime,
                "symbol": symbol,
                "limit": limit,
                "cursor": cursor,
                "endTime": endTime,
            },
        )

    def get_asset_settlement_record(
        self,
        category: str = None,
        orderFilter: str = None,
        symbol: str = None,
    ) -> Dict[str, Any]:
        """
        settlement-record
        Parameters:
        :param category: No description.
            Type:str
        :param orderFilter: No description.
            Type:str
        :param symbol: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/settlement-record",
            params={
                "category": category,
                "orderFilter": orderFilter,
                "symbol": symbol,
            },
        )

    def get_ins_loan_ltv(
        self,
        currency: str = None,
        startTime: str = None,
        endTime: str = None,
        limit: float = None,
        cursor: str = None,
        orderLinkId: str = None,
        orderStatus: str = None,
    ) -> Dict[str, Any]:
        """
        Get Repay Orders
        Parameters:
        :param currency: No description.
            Type:str
        :param startTime: No description.
            Type:str
        :param endTime: No description.
            Type:str
        :param limit: No description.
            Type:float
        :param cursor: No description.
            Type:str
        :param orderLinkId: No description.
            Type:str
        :param orderStatus: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/ins-loan/ltv",
            params={
                "currency": currency,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "cursor": cursor,
                "orderLinkId": orderLinkId,
                "orderStatus": orderStatus,
            },
        )

    def get_account_wallet_balance(
        self,
        coin: str = None,
        accountType: str = None,
    ) -> pd.DataFrame:
        """
        Get Margin Coin Info
        Parameters:
        :param coin: No description.
            Type:str
        :param accountType: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        data = self._request(
            method="GET",
            path="/v5/account/wallet-balance",
            params={
                "coin": coin,
                "accountType": accountType,
            },
        )
        return account_wallet_balance_response_to_dataframe(data)

    def get_asset_coin_greeks(
        self,
        baseCoin: str = None,
        coin: str = None,
        qty: float = None,
        timeInForce: str = None,
        positionIdx: str = None,
        orderLinkId: str = None,
        orderStatus: str = None,
    ) -> Dict[str, Any]:
        """
        coin-greeks
        Parameters:
        :param baseCoin: No description.
            Type:str
        :param coin: No description.
            Type:str
        :param qty: No description.
            Type:float
        :param timeInForce: No description.
            Type:str
        :param positionIdx: No description.
            Type:str
        :param orderLinkId: No description.
            Type:str
        :param orderStatus: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/coin-greeks",
            params={
                "baseCoin": baseCoin,
                "coin": coin,
                "qty": qty,
                "timeInForce": timeInForce,
                "positionIdx": positionIdx,
                "orderLinkId": orderLinkId,
                "orderStatus": orderStatus,
            },
        )

    def get_account_collateral_info(
        self,
        currency: str = None,
    ) -> Dict[str, Any]:
        """
        collateral-info
        Parameters:
        :param currency: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/account/collateral-info",
            params={
                "currency": currency,
            },
        )

    def get_account_info(
        self,
        baseCoin: str = None,
        coin: str = None,
        unifiedMarginStatus: str = None,
        qty: float = None,
        timeInForce: str = None,
        positionIdx: str = None,
        orderLinkId: str = None,
        orderStatus: str = None,
    ) -> Dict[str, Any]:
        """
        account/info
        Parameters:
        :param baseCoin: No description.
            Type:str
        :param coin: No description.
            Type:str
        :param unifiedMarginStatus: No description.
            Type:str
        :param qty: No description.
            Type:float
        :param timeInForce: No description.
            Type:str
        :param positionIdx: No description.
            Type:str
        :param orderLinkId: No description.
            Type:str
        :param orderStatus: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/account/info",
            params={
                "baseCoin": baseCoin,
                "coin": coin,
                "unifiedMarginStatus ": unifiedMarginStatus,
                "qty": qty,
                "timeInForce": timeInForce,
                "positionIdx": positionIdx,
                "orderLinkId": orderLinkId,
                "orderStatus": orderStatus,
            },
        )

    def get_account_fee_rate(
        self,
        baseCoin: str = None,
        coin: str = None,
        unifiedMarginStatus: str = None,
        qty: float = None,
        timeInForce: str = None,
        positionIdx: str = None,
        orderLinkId: str = None,
        orderStatus: str = None,
    ) -> Dict[str, Any]:
        """
        fee-rate
        Parameters:
        :param baseCoin: No description.
            Type:str
        :param coin: No description.
            Type:str
        :param unifiedMarginStatus: No description.
            Type:str
        :param qty: No description.
            Type:float
        :param timeInForce: No description.
            Type:str
        :param positionIdx: No description.
            Type:str
        :param orderLinkId: No description.
            Type:str
        :param orderStatus: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/account/fee-rate",
            params={
                "baseCoin": baseCoin,
                "coin": coin,
                "unifiedMarginStatus ": unifiedMarginStatus,
                "qty": qty,
                "timeInForce": timeInForce,
                "positionIdx": positionIdx,
                "orderLinkId": orderLinkId,
                "orderStatus": orderStatus,
            },
        )

    def get_account_transaction_log(
        self,
        accountType: str = None,
        category: str = None,
        side: str = None,
        qty: float = None,
        timeInForce: str = None,
        positionIdx: str = None,
        orderLinkId: str = None,
        orderStatus: str = None,
    ) -> Dict[str, Any]:
        """
        transaction-log
        Parameters:
        :param accountType: No description.
            Type:str
        :param category: No description.
            Type:str
        :param side: No description.
            Type:str
        :param qty: No description.
            Type:float
        :param timeInForce: No description.
            Type:str
        :param positionIdx: No description.
            Type:str
        :param orderLinkId: No description.
            Type:str
        :param orderStatus: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/account/transaction-log",
            params={
                "accountType": accountType,
                "category": category,
                "side": side,
                "qty": qty,
                "timeInForce": timeInForce,
                "positionIdx": positionIdx,
                "orderLinkId": orderLinkId,
                "orderStatus": orderStatus,
            },
        )

    def get_account_borrow_history(
        self,
        currency: str = None,
        startTime: str = None,
        endTime: str = None,
        limit: float = None,
        cursor: str = None,
        category: str = None,
        orderLinkId: str = None,
        orderStatus: str = None,
    ) -> Dict[str, Any]:
        """
        borrow-history
        Parameters:
        :param currency: No description.
            Type:str
        :param startTime: No description.
            Type:str
        :param endTime: No description.
            Type:str
        :param limit: No description.
            Type:float
        :param cursor: No description.
            Type:str
        :param category: No description.
            Type:str
        :param orderLinkId: No description.
            Type:str
        :param orderStatus: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/account/borrow-history",
            params={
                "currency": currency,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
                "cursor": cursor,
                "category": category,
                "orderLinkId": orderLinkId,
                "orderStatus": orderStatus,
            },
        )

    def post_account_upgrade_to_uta(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        upgrade-to-uta
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/account/upgrade-to-uta", params={}, body=body
        )

    def post_account_set_margin_mode(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        set-margin-mode
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/account/set-margin-mode", params={}, body=body
        )

    def post_account_mmp_modify(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        set mmp
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/account/mmp-modify", params={}, body=body
        )

    def post_account_mmp_reset(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        reset mmp
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/account/mmp-reset", params={}, body=body
        )

    def post_order_disconnected_cancel_all(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        disconnected-cancel-all
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/v5/order/disconnected-cancel-all",
            params={},
            body=body,
        )

    def get_spot_lever_token_info(
        self,
        ltCoin: str = None,
    ) -> Dict[str, Any]:
        """
        spot-lever-token/info
        Parameters:
        :param ltCoin: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/spot-lever-token/info",
            params={
                "ltCoin": ltCoin,
            },
        )

    def get_spot_lever_token_reference(
        self,
        ltCoin: str = None,
    ) -> Dict[str, Any]:
        """
        spot-lever-token/reference
        Parameters:
        :param ltCoin: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/spot-lever-token/reference",
            params={
                "ltCoin": ltCoin,
            },
        )

    def post_spot_lever_token_purchase(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        spot-lever-token/purchase
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/spot-lever-token/purchase", params={}, body=body
        )

    def post_spot_lever_token_redeem(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        spot-lever-token/redeem
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/spot-lever-token/redeem", params={}, body=body
        )

    def get_spot_lever_token_order_record(
        self,
        api_key: str = None,
        timestamp: str = None,
        sign: str = None,
    ) -> Dict[str, Any]:
        """
        spot-lever-token/order-record
        Parameters:
        :param api_key: No description.
            Type:str
        :param timestamp: No description.
            Type:str
        :param sign: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/spot-lever-token/order-record",
            params={
                "api_key": api_key,
                "timestamp": timestamp,
                "sign": sign,
            },
        )

    def post_spot_margin_trade_switch_mode(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        spot-margin-trade/switch-mode
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/v5/spot-margin-trade/switch-mode",
            params={},
            body=body,
        )

    def post_spot_margin_trade_set_leverage(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        spot-margin-trade/set-leverage
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/v5/spot-margin-trade/set-leverage",
            params={},
            body=body,
        )

    def post_user_create_sub_member(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        Create Sub UID
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/user/create-sub-member", params={}, body=body
        )

    def post_user_create_sub_api(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        Create SubUid apikey (use exist master api key)
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/user/create-sub-api", params={}, body=body
        )

    def get_user_query_sub_members(
        self,
    ) -> Dict[str, Any]:
        """
        get Sub members list
        Parameters:.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/user/query-sub-members",
            params={},
        )

    def get_user_query_api(
        self,
    ) -> Dict[str, Any]:
        """
        query uid's apikey info
        Parameters:.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/user/query-api",
            params={},
        )

    def post_user_frozen_sub_member(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        Froze Sub UID
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/user/frozen-sub-member", params={}, body=body
        )

    def post_user_update_api(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        Modify Master uid's api key permission
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/user/update-api", params={}, body=body
        )

    def post_user_delete_api(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        delete master uid apikey
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/user/delete-api", params={}, body=body
        )

    def post_user_update_sub_api(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        Modify sub uid's api key permission
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/user/update-sub-api", params={}, body=body
        )

    def post_user_delete_sub_api(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        delete sub uid apikey (use the api key pending to remove)
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/user/delete-sub-api", params={}, body=body
        )

    def get_asset_deposit_query_address(
        self,
        coin: str = None,
    ) -> Dict[str, Any]:
        """
        deposit/query-address
        Parameters:
        :param coin: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/deposit/query-address",
            params={
                "coin": coin,
            },
        )

    def get_asset_deposit_query_allowed_list(
        self,
    ) -> Dict[str, Any]:
        """
        deposit/query-allowed-list.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/deposit/query-allowed-list",
        )

    def get_asset_deposit_query_record(
        self,
    ) -> Dict[str, Any]:
        """
        deposit/query-record
        Parameters:.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/deposit/query-record",
            params={},
        )

    def get_asset_deposit_query_sub_member_address(
        self,
        coin: str = None,
        chainType: str = None,
        subMemberId: int = None,
    ) -> Dict[str, Any]:
        """
        deposit/query-sub-member-address
        Parameters:
        :param coin: No description.
            Type:str
        :param chainType: No description.
            Type:str
        :param subMemberId: No description.
            Type:int.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/deposit/query-sub-member-address",
            params={
                "coin": coin,
                "chainType": chainType,
                "subMemberId": subMemberId,
            },
        )

    def get_asset_deposit_query_sub_member_record(
        self,
        subMemberId: int = None,
    ) -> Dict[str, Any]:
        """
        deposit/query-sub-member-record
        Parameters:
        :param subMemberId: No description.
            Type:int.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/deposit/query-sub-member-record",
            params={
                "subMemberId": subMemberId,
            },
        )

    def get_asset_exchange_order_record(
        self,
        limit: int = None,
    ) -> Dict[str, Any]:
        """
        exchange/order-record
        Parameters:
        :param limit: No description.
            Type:int.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/exchange/order-record",
            params={
                "limit": limit,
            },
        )

    def get_asset_transfer_query_account_coin_balance(
        self,
        accountType: str = None,
        coin: str = None,
    ) -> Dict[str, Any]:
        """
        transfer/query-account-coin-balance
        Parameters:
        :param accountType: No description.
            Type:str
        :param coin: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/transfer/query-account-coin-balance",
            params={
                "accountType": accountType,
                "coin": coin,
            },
        )

    def get_asset_transfer_query_account_coins_balance(
        self,
        accountType: str = None,
        coin: str = None,
    ) -> Dict[str, Any]:
        """
        transfer/query-account-coins-balance
        Parameters:
        :param accountType: No description.
            Type:str
        :param coin: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/transfer/query-account-coins-balance",
            params={
                "accountType": accountType,
                "coin": coin,
            },
        )

    def get_asset_transfer_query_asset_info(
        self,
        accountType: str = None,
    ) -> Dict[str, Any]:
        """
        transfer/query-asset-info
        Parameters:
        :param accountType: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/transfer/query-asset-info",
            params={
                "accountType": accountType,
            },
        )

    def get_asset_coin_query_info(
        self,
        coin: str = None,
    ) -> Dict[str, Any]:
        """
        coin/query-info
        Parameters:
        :param coin: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/coin/query-info",
            params={
                "coin": coin,
            },
        )

    def get_asset_transfer_query_sub_member_list(
        self,
    ) -> Dict[str, Any]:
        """
        transfer/query-sub-member-list
        Parameters:.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/transfer/query-sub-member-list",
            params={},
        )

    def get_asset_transfer_query_inter_transfer_list(
        self,
    ) -> Dict[str, Any]:
        """
        transfer/query-inter-transfer-list
        Parameters:.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/transfer/query-inter-transfer-list",
            params={},
        )

    def get_asset_transfer_query_universal_transfer_list(
        self,
    ) -> Dict[str, Any]:
        """
        transfer/query-universal-transfer-list
        Parameters:.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/transfer/query-universal-transfer-list",
            params={},
        )

    def post_asset_transfer_save_transfer_sub_member(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        transfer/save-transfer-sub-member
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/v5/asset/transfer/save-transfer-sub-member",
            params={},
            body=body,
        )

    def get_asset_transfer_query_transfer_coin_list(
        self,
        fromAccountType: str = None,
        toAccountType: str = None,
    ) -> Dict[str, Any]:
        """
        transfer/query-transfer-coin-list
        Parameters:
        :param fromAccountType: No description.
            Type:str
        :param toAccountType: No description.
            Type:str.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/transfer/query-transfer-coin-list",
            params={
                "fromAccountType": fromAccountType,
                "toAccountType": toAccountType,
            },
        )

    def post_asset_transfer_inter_transfer(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        transfer/inter-transfer
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/v5/asset/transfer/inter-transfer",
            params={},
            body=body,
        )

    def post_asset_transfer_universal_transfer(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        transfer/universal-transfer
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST",
            path="/v5/asset/transfer/universal-transfer",
            params={},
            body=body,
        )

    def get_asset_withdraw_query_record(
        self,
    ) -> Dict[str, Any]:
        """
        withdraw/query-record
        Parameters:.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="GET",
            path="/v5/asset/withdraw/query-record",
            params={},
        )

    def post_asset_withdraw_create(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        withdraw/create
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/asset/withdraw/create", params={}, body=body
        )

    def post_asset_withdraw_cancel(
        self,
        body: dict = None,
    ) -> Dict[str, Any]:
        """
        withdraw/cancel
        Parameters:
        :param body: Request body.
            Type: dict.
        :returns: Successful response
        :raises: Any exceptions raised by the `requests` library.
        """
        return self._request(
            method="POST", path="/v5/asset/withdraw/cancel", params={}, body=body
        )
