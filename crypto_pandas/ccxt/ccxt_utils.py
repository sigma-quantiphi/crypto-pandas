import pandas as pd


def merge_markets_with_balances(
    markets: pd.DataFrame, balance: pd.DataFrame
) -> pd.DataFrame:
    for column in ["base", "quote", "settle"]:
        column_renaming = {
            x: f"{column}_{x}" for x in ["free", "used", "total", "debt"]
        }
        markets = markets.merge(balance.rename(columns={"symbol": column})).rename(
            columns=column_renaming
        )
    return markets
