import numpy as np
import pandas as pd


def date_time_columns_to_int(data: pd.DataFrame) -> pd.DataFrame:
    columns = (
        data.select_dtypes("datetimetz").columns.tolist()
        + data.select_dtypes("datetime").columns.tolist()
    )
    data[columns] = (data[columns].astype("int64") // 10**6).astype(str)
    return data


def expand_dict_columns(data: pd.DataFrame, separator: str = ".") -> pd.DataFrame:
    data = data.reset_index(drop=True)
    dict_columns = [
        x for x in data.columns if all(data[x].apply(lambda y: isinstance(y, dict)))
    ]
    columns_list = [data.drop(columns=dict_columns).copy()]
    for dict_column in dict_columns:
        exploded_column = pd.json_normalize(data[dict_column])
        exploded_column.columns = [
            f"{dict_column}{separator}{x}" for x in exploded_column.columns
        ]
        columns_list.append(exploded_column.copy())
    return pd.concat(columns_list, axis=1)


def combine_params(row: pd.Series, param_cols: list) -> dict:
    return {
        column.replace("params.", ""): row[column]
        for column in param_cols
        if pd.notnull(row[column])
    }


def format_value(value: float, step_size: float = 0.001) -> str:
    """Rounds the data according to the provided step size"""
    if step_size >= 1:
        formatted_value = str(int(round(value / step_size) * step_size))
    else:
        decimals = abs(int(np.log10(step_size)))
        formatted_value = f"{value:.{decimals}f}"
    return formatted_value


def format_orders(orders: pd.DataFrame, quantity_field_name: str = "quantity") -> list:
    data = orders.copy()
    data = date_time_columns_to_int(data)
    data[quantity_field_name] = data.apply(
        lambda x: format_value(x[quantity_field_name], x["stepSize"]), axis=1
    )
    if "price" in data.columns:
        data["price"] = data.apply(
            lambda x: format_value(x["price"], x["tickSize"]), axis=1
        )
    return data.drop(columns=["stepSize", "tickSize"]).to_dict("records")
