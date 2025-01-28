import pandas as pd


def calculate_max_end_date(
    start_date: pd.Timestamp, limit: int = 1000, interval: str = "1h"
) -> pd.Timestamp:
    end_date = start_date + limit * pd.Timedelta(interval)
    return end_date
