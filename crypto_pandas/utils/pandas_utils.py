import pandas as pd


def preprocess_dataframe(
    data: pd.DataFrame,
    int_datetime_columns: set = None,
    str_datetime_columns: set = None,
    numeric_columns: set = None,
) -> pd.DataFrame:
    if int_datetime_columns:
        datetime_columns_to_convert = [
            x for x in data.columns if x in int_datetime_columns
        ]
        data[datetime_columns_to_convert] = (
            data[datetime_columns_to_convert]
            .apply(pd.to_numeric)
            .apply(pd.to_datetime, unit="ms")
        )
    if str_datetime_columns:
        datetime_columns_to_convert = [
            x for x in data.columns if x in str_datetime_columns
        ]
        data[datetime_columns_to_convert] = data[datetime_columns_to_convert].apply(
            pd.to_datetime
        )
    if numeric_columns:
        numeric_columns_to_convert = [x for x in data.columns if x in numeric_columns]
        data[numeric_columns_to_convert] = data[numeric_columns_to_convert].apply(
            pd.to_numeric
        )
    return data
