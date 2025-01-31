import hmac
import hashlib
import time
from urllib.parse import urlencode

from crypto_pandas.hmac_authentication import generate_signature

API_KEY = "API_KEY"
SECRET_KEY = "SECRET_KEY"

req = {
    "id": 14,
    "method": "private/create-order-list",
    "api_key": API_KEY,
    "params": {
        "contingency_type": "LIST",
        "order_list": [
            {
                "instrument_name": "ONE_USDT",
                "side": "BUY",
                "type": "LIMIT",
                "price": "0.24",
                "quantity": "1.0",
            },
            {
                "instrument_name": "ONE_USDT",
                "side": "BUY",
                "type": "STOP_LIMIT",
                "price": "0.27",
                "quantity": "1.0",
                "trigger_price": "0.26",
            },
        ],
    },
    "nonce": int(time.time() * 1000),
}

# First ensure the params are alphabetically sorted by key
param_str = json.dumps(payload, separators=(",", ":"))  # Minify JSON


payload_str = (
    req["method"] + str(req["id"]) + req["api_key"] + param_str + str(req["nonce"])
)

req["sig"] = generate_signature(SECRET_KEY, payload_str)
