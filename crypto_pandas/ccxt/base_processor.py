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
from typing import Union, Literal

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
    - Handle cases where price or volume are out of range based on specific configurations.

    Attributes:
        exchange_name (str): Name of the exchange being processed (e.g., "binance").
        account_name (str): Name of the account associated with the API data.
        dropna_fields (bool): Determines whether empty (NaN) columns are removed from DataFrame outputs.
        order_schema (OrderSchema): Schema used to validate and process orders.
        amount_out_of_range (str): Defines behavior when volume exceeds acceptable ranges. Options include:
            - "warn": Logs a warning while removing the order.
            - "clip": Clips or limits the volume to valid ranges.
        price_out_of_range (str): Defines behavior when price exceeds allowable ranges. Options include:
            - "warn": Logs a warning while removing the order.
            - "clip": Adjusts the price to fit within predefined limits.
        conduct_order_checks (bool): Flag to enable or disable checks when converting orders to dictionary format.
        datetime_to_int_fields (tuple): Fields that should be converted from datetime to integer timestamps.
        int_to_datetime_fields (tuple): Fields to convert from integer timestamps to pandas datetime.
        str_to_datetime_fields (tuple): Fields with string timestamps to convert to pandas datetime.
        numeric_fields (tuple): Fields that should be cast to numeric types.
        bool_fields (tuple): Fields that should be cast to boolean types.
        ohlcv_fields (tuple): Standard OHLCV (Open, High, Low, Close, Volume) column names.
    """

    exchange_name: str = None
    account_name: str = None
    dropna_fields: bool = True
    order_schema: OrderSchema = field(default=OrderSchema)
    datetime_to_int_fields: tuple = None
    conduct_order_checks: bool = True
    amount_out_of_range: Literal["warn", "clip"] = "warn"
    price_out_of_range: Literal["warn", "clip"] = "warn"
    int_to_datetime_fields: tuple = (
        "createTime",
        "created",
        "createDate",
        "expiry",
        "expiryDate",
        "fundingTimestamp",
        "nextFundingTimestamp",
        "previousFundingTimestamp",
        "time",
        "timestamp",
        "updateTime",
    )
    str_to_datetime_fields: tuple = (
        "datetime",
        "expiryDatetime",
        "fundingDatetime",
        "nextFundingDatetime",
        "previousFundingDatetime",
    )
    numeric_fields: tuple = (
        "ask",
        "askImpliedVolatility",
        "askPrice",
        "askSize",
        "askVolume",
        "availableBalance",
        "average",
        "baseRate",
        "baseVolume",
        "bid",
        "bidImpliedVolatility",
        "bidPrice",
        "bidSize",
        "bidVolume",
        "buySellRatio",
        "buyVol",
        "change",
        "close",
        "collateral",
        "collateralMarginLevel",
        "contractSize",
        "contracts",
        "crossUnPnl",
        "crossWalletBalance",
        "delta",
        "entryPrice",
        "estimatedSettlePrice",
        "exercisePrice",
        "fee_cost",
        "fee_currency",
        "free",
        "freeze",
        "fundingRate",
        "gamma",
        "indexPrice",
        "initialMargin",
        "initialMarginPercentage",
        "last",
        "lastPrice",
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
        "markImpliedVolatility",
        "markPrice",
        "maxNotional",
        "maxWithdrawAmount",
        "nextFundingRate",
        "notional",
        "open",
        "openOrderInitialMargin",
        "percentage",
        "period",
        "positionAmount",
        "positionInitialMargin",
        "previousClose",
        "previousFundingRate",
        "price",
        "quantity",
        "quoteRate",
        "quoteVolume",
        "realStrikePrice",
        "rho",
        "sellVol",
        "shortAccount",
        "strike",
        "strikePrice",
        "theta",
        "totalAssetOfBtc",
        "totalCollateralValueInUSDT",
        "totalLiabilityOfBtc",
        "totalNetAssetOfBtc",
        "underlyingPrice",
        "unrealizedPnl",
        "unrealizedProfit",
        "vega",
        "vwap",
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

    def preprocess_dict(self, data: dict) -> dict:
        """
        Preprocess a dictionary by converting fields based on their type definitions.

        Args:
            data (dict): A dictionary containing raw API data.

        Returns:
            dict: A dictionary with properly formatted fields.
        """
        new_data = {}
        for key, value in data.items():
            if self.int_to_datetime_fields and (key in self.int_to_datetime_fields):
                value = pd.Timestamp(pd.to_numeric(value), unit="ms", tz="UTC")
            elif self.str_to_datetime_fields and (key in self.str_to_datetime_fields):
                value = pd.Timestamp(value, tz="UTC")
            elif self.numeric_fields and (key in self.numeric_fields):
                value = pd.to_numeric(value, errors="coerce")
            if pd.notnull(value):
                new_data[key] = value
        if self.exchange_name:
            new_data["exchange"] = self.exchange_name
        if self.account_name:
            new_data["account"] = self.account_name
        return new_data

    def preprocess_dataframe(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess a DataFrame by converting fields based on their types.

        Args:
            data (pd.DataFrame): The DataFrame to preprocess.

        Returns:
            pd.DataFrame: A processed DataFrame with formatted columns.
        """
        columns = data.columns
        data = expand_dict_columns(
            data.drop(columns=["info"], errors="ignore"), separator="_"
        )
        if self.int_to_datetime_fields:
            datetime_columns_to_convert = [
                x for x in columns if x in self.int_to_datetime_fields
            ]
            if datetime_columns_to_convert:
                data[datetime_columns_to_convert] = (
                    data[datetime_columns_to_convert]
                    .apply(pd.to_numeric, errors="coerce")
                    .apply(pd.to_datetime, unit="ms", utc=True, errors="coerce")
                )
        if self.str_to_datetime_fields:
            datetime_columns_to_convert = [
                x for x in columns if x in self.str_to_datetime_fields
            ]
            if datetime_columns_to_convert:
                data[datetime_columns_to_convert] = data[datetime_columns_to_convert].apply(
                    pd.to_datetime, utc=True, errors="coerce"
                )
        if self.numeric_fields:
            numeric_columns_to_convert = [
                x for x in columns if x in self.numeric_fields
            ]
            if numeric_columns_to_convert:
                data[numeric_columns_to_convert] = data[numeric_columns_to_convert].apply(
                    pd.to_numeric, errors="coerce"
                )
        if self.bool_fields:
            bool_columns_to_convert = [x for x in columns if x in self.bool_fields]
            if bool_columns_to_convert:
                data[bool_columns_to_convert] = data[bool_columns_to_convert].astype(bool)
        if self.dropna_fields:
            data = data.dropna(axis=1, how="all")
        if self.exchange_name:
            data["exchange"] = self.exchange_name
        if self.account_name:
            data["account"] = self.account_name
        return data

    def response_to_dataframe(
        self, data: list | dict, column_names: tuple = None
    ) -> pd.DataFrame:
        """
                Convert a list of dictionaries into a pandas DataFrame and preprocess it.

                Args:
                    data (list): Raw data returned from the API.
                    column_names (tuple, optional): Column names for the DataFrame.
        symbol (str): The trading pair (e.g., "BTC/USDT") associated with the OHLCV data.
                Returns:
                    pd.DataFrame: A preprocessed DataFrame.
        """
        data = pd.DataFrame(data=data)
        if column_names:
            data.columns = column_names
        return self.preprocess_dataframe(data)

    def markets_to_dataframe(self, data: dict) -> pd.DataFrame:
        return self.preprocess_dataframe(pd.DataFrame(data).transpose())

    def balance_to_dataframe(self, data: dict) -> pd.DataFrame:
        if "total" in data:
            df = pd.DataFrame(data={"symbol": list(data["total"].keys())})
            for column in ["free", "used", "total", "debt"]:
                if column in data:
                    df[column] = df["symbol"].map(data[column])
        else:
            df = pd.DataFrame(data={"symbol": data.keys()})
            df = df.query("~(symbol in ['info', 'timestamp', 'datetime'])").reset_index(
                drop=True
            )
            df["base"] = df["symbol"].str.split("/").str[0]
            df["quote"] = df["symbol"].str.split("/").str[1]
            for index, row in df.iterrows():
                for x in ["base", "quote"]:
                    for column in ["free", "used", "total", "debt"]:
                        symbol_data = data[row["symbol"]]
                        if column in symbol_data:
                            df.loc[index, f"{x}_{column}"] = symbol_data[row[x]][column]
        if "timestamp" in data:
            df["timestamp"] = data["timestamp"]
        if "datetime" in data:
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
        if not data.empty:
            data = self.preprocess_dataframe(data)
        return data

    def order_books_to_dataframe(self, data: dict) -> pd.DataFrame:
        """
        Convert order book data for multiple symbols into a unified pandas DataFrame.

        Args:
            data (dict): A dictionary containing order book data for multiple symbols.
                         Each key is a symbol, and the value is the corresponding
                         order book data.

        Returns:
            pd.DataFrame: A preprocessed DataFrame containing combined order book information
                          for all symbols, including price, quantity, and metadata.
        """
        df = []
        for symbol, symbol_data in data.items():
            symbol_data = self.order_book_to_dataframe(symbol_data)
            if not symbol_data.empty:
                symbol_data["symbol"] = symbol
                df.append(symbol_data.copy())
        return pd.concat(df, ignore_index=True)

    def ohlcv_to_dataframe(self, data: list, symbol: str | None = None) -> pd.DataFrame:
        """
        Convert OHLCV data into a pandas DataFrame.

        Args:
            data (list): List containing OHLCV data.
            symbol (str | None): The trading pair (e.g., "BTC/USDT") associated with the OHLCV data, if applicable.

        Returns:
            pd.DataFrame: A preprocessed OHLCV DataFrame.
        """
        data = self.response_to_dataframe(data, column_names=self.ohlcv_fields)
        if symbol:
            data["symbol"] = symbol
        return data

    def ohlcv_symbols_to_dataframe(self, data: dict) -> pd.DataFrame:
        """
        Convert OHLCV data for multiple trading pairs into a pandas DataFrame.

        Args:
            data (dict): Dictionary containing OHLCV data, where keys are symbols
                         and sub-keys are timeframes.

        Returns:
            pd.DataFrame: A preprocessed DataFrame containing OHLCV data with symbol
                          and timeframe columns for each trading pair.
        """
        full_data = []
        for symbol, timeframes in data.items():
            for timeframe, ohlcv_data in timeframes.items():
                df = self.ohlcv_to_dataframe(data=ohlcv_data, symbol=symbol)
                df["timeframe"] = timeframe
                full_data.append(df.copy())
        return pd.concat(full_data, ignore_index=True)

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
