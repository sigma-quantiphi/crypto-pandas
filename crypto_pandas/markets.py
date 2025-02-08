from typing import Union

import pandas as pd

from ccxt_pandas.preprocessing import preprocess_dataframe, response_to_dataframe


def depth_to_dataframe(data: Union[dict, list]) -> pd.DataFrame:
    dfs = []
    for x in ["asks", "bids"]:
        df = pd.json_normalize(
            data=data,
            record_path=x,
            meta=["symbol", "timestamp", "datetime", "nonce", "exchange"],
            errors="ignore",
        )
        df["side"] = x
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True).rename(columns={0: "price", 1: "qty"})
    return preprocess_dataframe(data)


def ohlcv_to_dataframe(data: list) -> pd.DataFrame:
    column_names = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]
    return response_to_dataframe(data, column_names=column_names)
