import base64

import time
import hashlib
import hmac

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


def auth(
    api_key: str,
    api_secret: str,
    params: dict = None,
    recv_window: int = 5000,
    use_rsa_authentication: bool = False,
) -> dict:
    # Create a query string
    if params:
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    else:
        query_string = ""
    timestamp = int(time.time() * 10**3)
    param_str = f"{timestamp}{api_key}{recv_window}{query_string}"
    if use_rsa_authentication:
        signature = SHA256.new(param_str.encode("utf-8"))
        signature = base64.b64encode(
            PKCS1_v1_5.new(RSA.importKey(api_secret)).sign(signature)
        )
        signature = signature.decode()
    else:
        signature = hmac.new(
            bytes(api_secret, "utf-8"), param_str.encode("utf-8"), hashlib.sha256
        ).hexdigest()
    headers = {
        "X-BAPI-API-KEY": api_key,
        "X-BAPI-SIGN": signature,
        "X-BAPI-SIGN-TYPE": "2",
        "X-BAPI-TIMESTAMP": str(timestamp),
        "X-BAPI-RECV-WINDOW": str(recv_window),
    }
    return headers
