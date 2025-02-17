from urllib.parse import urlencode
import time
from crypto_pandas.utils.requests import generate_signature, prepare_requests_parameters

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


def _encode_params(params: dict, special: bool = False) -> str:
    if special:
        return urlencode(params).replace("%40", "@").replace("%27", "%22")
    else:
        return urlencode(params, doseq=True).replace("%40", "@")


def prepare_and_sign_parameters(
    secret: str, params: dict = None, recv_window: int = 5000
) -> str:
    if params:
        params = prepare_requests_parameters_binance(params)
    else:
        params = {}
    params["recvWindow"] = recv_window
    params["timestamp"] = int(time.time() * 1000)
    query_string = _encode_params(params, special=True)
    params["signature"] = generate_signature(secret, query_string)
    return _encode_params(params, special=True)
