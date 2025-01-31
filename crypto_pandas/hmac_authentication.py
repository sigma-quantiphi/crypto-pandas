import time
import hashlib
import hmac


def generate_signature(api_secret: str, query_string: str) -> str:
    """Signs request using HMAC-SHA256"""
    return hmac.new(
        api_secret.encode(), query_string.encode(), hashlib.sha256
    ).hexdigest()


def auth(
    api_key: str,
    api_secret: str,
    params: dict = None,
    recv_window: int = 5000,
    timestamp_units: int = 1000,
) -> dict:
    # Create a query string
    if params:
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    else:
        query_string = ""
    timestamp = int(time.time() * timestamp_units)
    param_str = f"{timestamp}{api_key}{recv_window}{query_string}"
    signature = hmac.new(
        api_secret.encode("utf-8"), param_str.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return {"signature": signature, "recv_window": recv_window, "timestamp": timestamp}


BASE_URL = "https://api.coinbase.com"

# Define the request details
request_path = "/v2/accounts"
method = "GET"
body = ""  # Empty for GET requests
timestamp = str(int(time.time()))  # Current timestamp in seconds

# Create the signature
message = timestamp + method + request_path + body
