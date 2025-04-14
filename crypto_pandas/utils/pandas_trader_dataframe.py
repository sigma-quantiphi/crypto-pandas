import pandas as pd


@pd.api.extensions.register_dataframe_accessor("pt")
class PandasTraderDataFrameAccessor:
    def __init__(self, pandas_obj):
        self.data = pandas_obj

    def create_buy_and_sell_orders(
        self, sides: tuple = ("buy", "sell")
    ) -> pd.DataFrame:
        dfs = []
        data = self.data.copy()
        for side in sides:
            data["side"] = side
            dfs.append(data.copy())
        return pd.concat(dfs)

    def is_ask(self) -> pd.Series:
        return self.data["side"] == "asks"

    def sign(self) -> pd.Series:
        return 2 * self.is_ask() - 1

    def signed_price(self) -> pd.Series:
        return self.sign() * self.data["price"]

    def sort_depth(self, by_exchange: bool = False) -> pd.DataFrame:
        data = self.data.copy()
        data["signed_price"] = self.signed_price()
        sort_columns = ["symbol", "side", "signed_price"]
        if by_exchange:
            sort_columns = ["exchange"] + sort_columns
        return data.sort_values(sort_columns, ignore_index=True)

    def notional(self) -> pd.Series:
        return self.data["price"] * self.data["qty"]

    def orderbook_waps(self, depths: list | tuple | set) -> pd.DataFrame:
        group_columns = ["symbol", "side"]
        if "exchange" in self.data.columns:
            group_columns.append("exchange")
        group_columns_depth = group_columns + ["depth"]
        data = self.data.copy()
        data["notional"] = self.notional()
        data["cum_notional"] = data.groupby(group_columns)["notional"].cumsum()
        waps = []
        for depth in depths:
            data["depth"] = depth
            waps.append(data.copy())
        waps = pd.concat(waps).query("(cum_notional - notional) <= depth")
        waps["notional"] = waps["notional"].where(
            waps["cum_notional"] <= waps["depth"],
            other=(
                waps["depth"]
                - waps.groupby(group_columns_depth)["cum_notional"].shift(1)
            ).fillna(waps["depth"]),
        )
        waps["qty"] = waps["notional"] / waps["price"]
        waps = waps.groupby(group_columns_depth, as_index=False)[
            ["qty", "notional"]
        ].sum()
        waps["price"] = waps["notional"] / waps["qty"]
        return waps

    def exchange_arbitrage(self) -> pd.DataFrame:
        data = self.data[["price", "qty", "side", "symbol", "exchange"]].copy()
        bids = data.query("side == 'bids'").drop(columns=["side"])
        asks = data.query("side == 'asks'").drop(columns=["side"])
        data = asks.merge(bids, suffixes=("_asks", "_bids"), on="symbol").query(
            "exchange_asks != exchange_bids"
        )
        data["spread"] = data["price_bids"] - data["price_asks"]
        data["qty"] = data["qty_bids"].clip(upper=data["qty_asks"])
        data["relative_spread"] = data["spread"] / data[
            ["price_asks", "price_bids"]
        ].mean(axis=1)
        return data

    def triangular_search(self) -> pd.DataFrame:
        data = self.data[["price", "qty", "side", "symbol", "exchange"]].copy()
        assets = data["symbol"].str.split("/", expand=True)
        data["asset_0"] = assets[0]
        data["asset_1"] = assets[1]
        data["asset_sell"] = assets[0].where(data["side"] == "asks", assets[1])
        data["asset_buy"] = assets[0].where(data["side"] == "bids", assets[1])
        df = data.merge(
            data, left_on="asset_buy", right_on="asset_sell", suffixes=("_0", "_1")
        ).query("symbol_0 != symbol_1")
        data.columns = [f"{x}_2" for x in data.columns]
        df = (
            df.merge(data, left_on="asset_buy_1", right_on="asset_sell_2")
            .query("asset_sell_0 == asset_buy_2")
            .reset_index(drop=True)
        )
        max_price = df[["price_2", "price_1", "price_0"]].max(axis=1)
        min_price = df[["price_2", "price_1", "price_0"]].min(axis=1)
        median_price = df[["price_2", "price_1", "price_0"]].median(axis=1)
        df["spread"] = max_price - median_price / min_price
        df["relative_spread"] = df["spread"] / max_price
        df["arbitrage"] = df.index
        orders = df.drop_duplicates(subset=["relative_spread"], keep="first").melt(
            id_vars=["arbitrage", "spread", "relative_spread"]
        )
        variable = orders["variable"].str.split("_", expand=True)
        orders["variable"] = variable[0]
        orders["step"] = variable[1]
        orders = orders.query(
            "variable in ['exchange', 'price', 'qty', 'side', 'symbol']"
        )
        orders = (
            orders.pivot(
                index=["arbitrage", "spread", "relative_spread", "step"],
                values="value",
                columns="variable",
            )
            .reset_index()
            .sort_values(["relative_spread", "arbitrage", "step"])
        )
        return orders
