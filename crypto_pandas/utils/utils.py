from functools import wraps
from typing import Any

import pandas as pd


def timestamp_to_int(timestamp: pd.Timestamp) -> int:
    return int(timestamp.timestamp() * 1000)


def preprocess_dict(
    data: dict, int_datetime_columns: set, str_datetime_columns: set
) -> dict:
    for key, value in data.items():
        if key in int_datetime_columns:
            data[key] = pd.Timestamp(value, unit="ms")
        elif key in str_datetime_columns:
            data[key] = pd.Timestamp(value)
    return data


def calculate_end_date(
    start_date: pd.Timestamp,
    limit: int = 1000,
    timeframe: str = "1h",
    add_one_timeframe: bool = False,
) -> pd.Timestamp:
    if add_one_timeframe:
        limit += 1
    end_date = start_date + limit * pd.Timedelta(timeframe)
    return end_date


def calculate_intervals(
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    timeframe: str = "1h",
) -> int:
    return int((end_date - start_date) / pd.Timedelta(timeframe))


def load_date_range_chunks(
    append: bool = True,
    from_time_key: str = "from_time",
    to_time_key: str = "to_time",
    timeframe_key: str = "timeframe",
):

    def date_range_wrapper(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = kwargs[from_time_key]
            to_time = kwargs[to_time_key]
            limit = kwargs.get("limit", 1000)
            kwargs.pop(from_time_key)
            kwargs.pop(to_time_key)
            results = []
            while start_time < to_time:
                end_time = calculate_end_date(
                    start_date=start_time,
                    limit=limit,
                    timeframe=kwargs[timeframe_key],
                )
                end_time = min(end_time, to_time)
                kwargs["since"] = timestamp_to_int(start_time)
                kwargs["limit"] = calculate_intervals(
                    start_time, end_time, kwargs[timeframe_key]
                )
                result = func(*args, **kwargs)
                if append:
                    results.append(result)
                else:
                    results += result
                start_time = end_time
            return results

        return wrapper

    return date_range_wrapper


def expand_dict_columns(data: pd.DataFrame) -> pd.DataFrame:
    data = data.reset_index(drop=True)
    dict_columns = [
        x for x in data.columns if all(data[x].apply(lambda y: isinstance(y, dict)))
    ]
    columns_list = [data.drop(columns=dict_columns).copy()]
    for dict_column in dict_columns:
        exploded_column = pd.json_normalize(data[dict_column])
        exploded_column.columns = [
            f"{dict_column}.{x}" for x in exploded_column.columns
        ]
        columns_list.append(exploded_column.copy())
    return pd.concat(columns_list, axis=1)


def print_markdown(message: Any) -> None:
    if isinstance(message, pd.DataFrame):
        print(message.to_markdown(index=False))
    else:
        print(message)
