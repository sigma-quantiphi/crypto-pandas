import time
import hashlib
import hmac
from urllib.parse import urlencode


def generate_signature(api_secret: str, query_string: str) -> str:
    """Signs request using HMAC-SHA256"""
    return hmac.new(
        api_secret.encode(), query_string.encode(), hashlib.sha256
    ).hexdigest()


def sign_parameters(
    api_key: str,
    api_secret: str,
    params: dict = None,
    recv_window: int = 5000,
    recv_window_name: str = "recv_window",
    timestamp_units: int = 1000,
    timestamp_name: str = "timestamp",
) -> dict:
    if params:
        query_string = urlencode(params)
    else:
        query_string = ""
    timestamp = int(time.time() * timestamp_units)
    param_str = f"{timestamp}{api_key}{recv_window}{query_string}"
    signature = hmac.new(
        api_secret.encode("utf-8"), param_str.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return {
        "signature": signature,
        recv_window_name: recv_window,
        timestamp_name: timestamp,
    }
