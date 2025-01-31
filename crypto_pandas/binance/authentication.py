from urllib.parse import urlencode
import time

from crypto_pandas.binance.binance_requests import prepare_requests_parameters
from crypto_pandas.hmac_authentication import generate_signature


def sign_parameters(secret: str, params: dict) -> dict:
    query_string = urlencode(params)
    params["signature"] = generate_signature(secret, query_string)
    return params


def prepare_and_sign_parameters(
    secret: str, params: dict = None, recv_window: int = 5000
) -> dict:
    if params is not None:
        params = prepare_requests_parameters(params)
        params["recvWindow"] = recv_window
    else:
        params = {"recvWindow": recv_window}
    params["timestamp"] = int(time.time() * 1000)
    return sign_parameters(secret, params)
