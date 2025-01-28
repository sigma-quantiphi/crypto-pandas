import pandas as pd

datetime_columns = {"fundingTime", "openTime", "closeTime", "transferDate"}
numeric_columns = {
    "fundingRate",
    "markPrice",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quoteAssetVolume",
    "takerBuyBaseAssetVolume",
    "takerBuyQuoteAssetVolume",
}


def binance_response_to_dict(data: dict) -> dict:
    for key, value in data.items():
        if key in datetime_columns:
            data[key] = pd.Timestamp(value, unit="ms")
        if key in numeric_columns:
            data[key] = float(value)
    return data


def binance_response_to_dataframe(
    data: list, column_names: list = None
) -> pd.DataFrame:
    df = pd.DataFrame(data)
    if column_names:
        df.columns = column_names
    datetime_columns_to_convert = [x for x in df.columns if x in datetime_columns]
    df[datetime_columns_to_convert] = df[datetime_columns_to_convert].apply(
        pd.to_datetime, unit="ms"
    )
    numeric_columns_to_convert = [x for x in df.columns if x in numeric_columns]
    df[numeric_columns_to_convert] = df[numeric_columns_to_convert].apply(pd.to_numeric)
    return df
