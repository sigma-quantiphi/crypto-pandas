from functools import wraps

import pandas as pd


def timestamp_to_int(timestamp: pd.Timestamp) -> int:
    return int(timestamp.timestamp() * 1000)


def prepare_requests_parameters(params: dict) -> dict:
    params = {k: v for k, v in params.items() if v is not None}
    for x in [
        "startTime",
        "endTime",
        "beginTime",
        "subscriptionStartTime",
    ]:
        if x in params:
            params[x] = timestamp_to_int(params[x])
    return params


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


def load_date_range_chunks(append: bool = True):

    def date_range_wrapper(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = kwargs["from_time"]
            to_time = kwargs["to_time"]
            limit = kwargs.get("limit", 1000)
            kwargs.pop("from_time")
            kwargs.pop("to_time")
            results = []
            while start_time < to_time:
                end_time = calculate_end_date(
                    start_date=start_time,
                    limit=limit,
                    timeframe=kwargs["timeframe"],
                )
                end_time = min(end_time, to_time)
                kwargs["since"] = timestamp_to_int(start_time)
                kwargs["limit"] = calculate_intervals(
                    start_time, end_time, kwargs["timeframe"]
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
