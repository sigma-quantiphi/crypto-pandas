def date_range_wrapper(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = kwargs["startTime"]
        end_time = kwargs["endTime"]
        results = []
        while start_time < end_time:
            chunk_end_time = calculate_max_end_date(
                start_date=start_time, interval=kwargs.get("interval")
            )
            if chunk_end_time > end_time:
                chunk_end_time = end_time
            kwargs.update(
                {
                    "startTime": start_time,
                    "endTime": chunk_end_time,
                }
            )
            result = func(*args, **kwargs)
            results.append(result)
            start_time = chunk_end_time + pd.Timedelta(kwargs.get("interval"))
        return results

    return wrapper
