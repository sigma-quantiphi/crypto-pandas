import pandas as pd

from crypto_pandas.utils.pandas_utils import preprocess_dataframe
from crypto_pandas.utils.utils import expand_dict_columns, preprocess_dict

int_datetime_columns = {
    "timestamp",
}
str_datetime_columns = {
    "datetime",
}


def preprocess_dict_ccxt(data: dict) -> dict:
    return preprocess_dict(
        data,
        int_datetime_columns=int_datetime_columns,
        str_datetime_columns=str_datetime_columns,
    )


def preprocess_dataframe_ccxt(df: pd.DataFrame) -> pd.DataFrame:
    df = preprocess_dataframe(
        data=df,
        int_datetime_columns=int_datetime_columns,
        str_datetime_columns=str_datetime_columns,
    )
    return expand_dict_columns(df.drop(columns=["info"], errors="ignore"))


def response_to_dataframe(data: list, column_names: list = None) -> pd.DataFrame:
    df = pd.DataFrame(data)
    if column_names:
        df.columns = column_names
    return preprocess_dataframe(df)
