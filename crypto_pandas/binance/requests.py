from urllib.parse import urlencode
import time
from crypto_pandas.utils.requests import generate_signature

date_time_to_int_keys = {
    "startTime",
    "endTime",
    "beginTime",
    "subscriptionStartTime",
}


def prepare_requests_parameters_binance(data: dict) -> dict:
    return prepare_requests_parameters(
        data, date_time_to_int_keys=date_time_to_int_keys
    )


def prepare_and_sign_parameters(
    secret: str, params: dict = None, recv_window: int = 5000
) -> dict:
    if params:
        params = prepare_requests_parameters_binance(params)
        params["recvWindow"] = recv_window
    else:
        params = {"recvWindow": recv_window}
    params["timestamp"] = int(time.time() * 1000)
    query_string = urlencode(params)
    params["signature"] = generate_signature(secret, query_string)
    return params


def auth_request_binance(
    api_key: str, secret: str, params: dict = None, recv_window: int = 5000
) -> dict:
    params = prepare_and_sign_parameters(
        secret=secret, params=params, recv_window=recv_window
    )
    return {
        "params": params,
        "headers": {
            "X-MBX-APIKEY": api_key,
        },
    }
