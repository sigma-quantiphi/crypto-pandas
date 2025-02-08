import pandas as pd

int_datetime_columns = {
    "timestamp",
}
str_datetime_columns = {
    "datetime",
}


def expand_dict_columns(data: pd.DataFrame) -> pd.DataFrame:
    dict_columns = [
        x for x in data.columns if all(data[x].apply(lambda y: isinstance(y, dict)))
    ]
    columns_list = [data.drop(columns=dict_columns).copy()]
    for dict_column in dict_columns:
        exploded_column = pd.json_normalize(data[dict_column])
        exploded_column.columns = [f"{dict_column}.{x}" for x in exploded_column.columns]
        columns_list.append(exploded_column.copy())
    return pd.concat(columns_list, axis=1)


def preprocess_dict(data: dict) -> dict:
    for key, value in data.items():
        if key in int_datetime_columns:
            data[key] = pd.Timestamp(value, unit="ms")
        elif key in str_datetime_columns:
            data[key] = pd.Timestamp(value)
    return data


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    datetime_columns_to_convert = [x for x in df.columns if x in int_datetime_columns]
    df[datetime_columns_to_convert] = df[datetime_columns_to_convert].apply(
        pd.to_datetime, unit="ms", utc=True
    )
    datetime_columns_to_convert = [x for x in df.columns if x in str_datetime_columns]
    df[datetime_columns_to_convert] = df[datetime_columns_to_convert].apply(
        pd.to_datetime
    )
    return expand_dict_columns(df.drop(columns=["info"], errors="ignore"))


def response_to_dataframe(data: list, column_names: list = None) -> pd.DataFrame:
    df = pd.DataFrame(data)
    if column_names:
        df.columns = column_names
    return preprocess_dataframe(df)
