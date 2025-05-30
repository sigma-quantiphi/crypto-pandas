"""
BaseProcessor Module

This module defines the BaseProcessor class, which serves as a parent class for API data preprocessing.
It provides common preprocessing functionality for converting raw API responses into cleaned and formatted
pandas DataFrames. This class simplifies handling timestamps, numeric conversions, boolean casting,
and other common transformations needed for trading data, such as orders, order books, and OHLCV data.

Classes:
    BaseProcessor: Provides methods for preprocessing API responses from exchanges into pandas DataFrames.

Attributes:
    possible_depth_meta (list): List of potential metadata fields found in order book depth data.
"""

from dataclasses import dataclass, field
from typing import Union

import pandas as pd

from crypto_pandas.ccxt.order_schema import OrderSchema
from crypto_pandas.utils.pandas_utils import (
    expand_dict_columns,
    determine_mandatory_optional_fields_pandera,
)
from pandera.typing import DataFrame


possible_depth_meta = ["symbol", "timestamp", "datetime", "nonce", "exchange", "T", "u"]


@dataclass
class BaseProcessor:
    """
    CCXTProcessor is a parent class for handling preprocessing of API responses into pandas DataFrames.

    This class includes methods to:
    - Convert timestamps into datetime objects.
    - Normalize nested JSON responses.
    - Filter and format order data according to a schema.
    - Preprocess order books, trades, and OHLCV data.

    Attributes:
        order_schema (OrderSchema): Schema used to validate and process orders.
        datetime_to_int_fields (tuple): Fields that should be converted from datetime to integer timestamps.
        int_to_datetime_fields (tuple): Fields to convert from integer timestamps to pandas datetime.
        str_to_datetime_fields (tuple): Fields with string timestamps to convert to pandas datetime.
        numeric_fields (tuple): Fields that should be cast to numeric types.
        bool_fields (tuple): Fields that should be cast to boolean types.
        ohlcv_fields (tuple): Standard OHLCV (Open, High, Low, Close, Volume) column names.
    """

    order_schema: OrderSchema = field(default=OrderSchema)
    datetime_to_int_fields: tuple = None
    int_to_datetime_fields: tuple = (
        "createTime",
        "created",
        "expiry",
        "time",
        "timestamp",
        "updateTime",
    )
    str_to_datetime_fields: tuple = (
        "datetime",
        "expiryDatetime",
    )
    numeric_fields: tuple = (
        "availableBalance",
        "buySellRatio",
        "buyVol",
        "collateral",
        "collateralMarginLevel",
        "contractSize",
        "contracts",
        "crossUnPnl",
        "crossWalletBalance",
        "entryPrice",
        "free",
        "freeze",
        "initialMargin",
        "initialMarginPercentage",
        "leverage",
        "liquidationPrice",
        "locked",
        "longAccount",
        "longShortRatio",
        "maintMargin",
        "maintenanceMargin",
        "maintenanceMarginPercentage",
        "marginBalance",
        "marginLevel",
        "marginRatio",
        "markPrice",
        "maxNotional",
        "maxWithdrawAmount",
        "notional",
        "openOrderInitialMargin",
        "percentage",
        "positionAmount",
        "positionInitialMargin",
        "sellVol",
        "shortAccount",
        "strike",
        "totalAssetOfBtc",
        "totalCollateralValueInUSDT",
        "totalLiabilityOfBtc",
        "totalNetAssetOfBtc",
        "unrealizedPnl",
        "unrealizedProfit",
        "walletBalance",
        "withdrawing",
    )
    bool_fields: tuple = None
    ohlcv_fields: tuple = (
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    )
    conduct_order_checks: bool = True

    def preprocess_dict(self, data: dict) -> dict:
        """
        Preprocess a dictionary by converting fields based on their type definitions.

        Args:
            data (dict): A dictionary containing raw API data.

        Returns:
            dict: A dictionary with properly formatted fields.
        """
        for key, value in data.items():
            if self.int_to_datetime_fields and (key in self.int_to_datetime_fields):
                data[key] = pd.Timestamp(float(value), unit="ms")
            elif self.str_to_datetime_fields and (key in self.str_to_datetime_fields):
                data[key] = pd.Timestamp(value)
            elif self.numeric_fields and (key in self.numeric_fields):
                data[key] = pd.to_numeric(value, errors="coerce")
        return data

    def preprocess_dataframe(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess a DataFrame by converting fields based on their types.

        Args:
            data (pd.DataFrame): The DataFrame to preprocess.

        Returns:
            pd.DataFrame: A processed DataFrame with formatted columns.
        """
        columns = data.columns
        if self.int_to_datetime_fields:
            datetime_columns_to_convert = [
                x for x in columns if x in self.int_to_datetime_fields
            ]
            data[datetime_columns_to_convert] = (
                data[datetime_columns_to_convert]
                .apply(pd.to_numeric, errors="coerce")
                .apply(pd.to_datetime, unit="ms", utc=True, errors="coerce")
            )
        if self.str_to_datetime_fields:
            datetime_columns_to_convert = [
                x for x in columns if x in self.str_to_datetime_fields
            ]
            data[datetime_columns_to_convert] = data[datetime_columns_to_convert].apply(
                pd.to_datetime, utc=True, errors="coerce"
            )
        if self.numeric_fields:
            numeric_columns_to_convert = [
                x for x in columns if x in self.numeric_fields
            ]
            data[numeric_columns_to_convert] = data[numeric_columns_to_convert].apply(
                pd.to_numeric, errors="coerce"
            )
        if self.bool_fields:
            bool_columns_to_convert = [x for x in columns if x in self.bool_fields]
            data[bool_columns_to_convert] = data[bool_columns_to_convert].astype(bool)
        return expand_dict_columns(
            data.drop(columns=["info", "fees"], errors="ignore"), separator="_"
        )

    def response_to_dataframe(
        self, data: list, column_names: tuple = None
    ) -> pd.DataFrame:
        """
        Convert a list of dictionaries into a pandas DataFrame and preprocess it.

        Args:
            data (list): Raw data returned from the API.
            column_names (tuple, optional): Column names for the DataFrame.

        Returns:
            pd.DataFrame: A preprocessed DataFrame.
        """
        data = pd.DataFrame(data=data)
        if column_names:
            data.columns = column_names
        return self.preprocess_dataframe(data)

    def markets_to_dataframe(self, data: dict) -> pd.DataFrame:
        data = pd.DataFrame(list(data.values()))
        return self.preprocess_dataframe(data)

    def balance_to_dataframe(self, data: dict) -> pd.DataFrame:
        df = pd.DataFrame(data={"symbol": list(data["total"].keys())})
        for column in ["free", "used", "total", "debt"]:
            if column in data:
                df[column] = df["symbol"].map(data[column])
        df["timestamp"] = data["timestamp"]
        df["datetime"] = data["datetime"]
        return self.preprocess_dataframe(df)

    def order_book_to_dataframe(self, data: Union[dict, list]) -> pd.DataFrame:
        """
        Convert order book data into a pandas DataFrame.

        Args:
            data (Union[dict, list]): Raw order book data from the API.

        Returns:
            pd.DataFrame: A preprocessed order book DataFrame.
        """
        dfs = []
        if isinstance(data, list):
            keys = data[0].keys()
        else:
            keys = data.keys()
        meta = [x for x in keys if x in possible_depth_meta]
        for x in ["asks", "bids"]:
            df = pd.json_normalize(
                data=data,
                record_path=x,
                meta=meta,
            )
            df["side"] = x
            dfs.append(df)
        data = pd.concat(dfs, ignore_index=True).rename(
            columns={0: "price", 1: "qty", "T": "timestamp", "u": "updateId"}
        )
        return self.preprocess_dataframe(data)

    def ohlcv_to_dataframe(self, data: list) -> pd.DataFrame:
        """
        Convert OHLCV data into a pandas DataFrame.

        Args:
            data (list): List containing OHLCV data.

        Returns:
            pd.DataFrame: A preprocessed OHLCV DataFrame.
        """
        return self.response_to_dataframe(data, column_names=self.ohlcv_fields)

    def orders_to_dataframe(self, data: list) -> pd.DataFrame:
        """
        Convert order data into a pandas DataFrame.

        Args:
            data (list): A list of order dictionaries.

        Returns:
            pd.DataFrame: A preprocessed orders DataFrame.
        """
        trades = pd.json_normalize(
            data=data,
            record_path="trades",
            meta=[
                "id",
                "clientOrderId",
                "timestamp",
                "datetime",
                "lastTradeTimestamp",
                "lastUpdateTimestamp",
                "symbol",
                "type",
                "timeInForce",
                "postOnly",
                "reduceOnly",
                "side",
                "price",
                "triggerPrice",
                "amount",
                "cost",
                "average",
                "filled",
                "remaining",
                "status",
                "fee",
                "fees",
                "stopPrice",
                "takeProfitPrice",
                "stopLossPrice",
            ],
        )
        orders = pd.DataFrame(data=data)
        if not trades.empty:
            orders = orders.merge(trades, how="outer")
        return self.preprocess_dataframe(orders)

    def orders_to_dict(self, orders: pd.DataFrame) -> list:
        """
        Convert a DataFrame of orders into a list of dictionaries suitable for API submission.

        Args:
            orders (DataFrame): DataFrame containing order data.

        Returns:
            list: List of dictionaries representing orders.
        """
        if self.conduct_order_checks:
            self.order_schema.validate(orders)
        fields = determine_mandatory_optional_fields_pandera(self.order_schema)
        fields["optional"] = [x for x in orders.columns if x in fields["optional"]]
        return orders[fields["mandatory"] + fields["optional"]].to_dict("records")
