import time
import hmac
import base64
import json
import requests
from typing import Optional, Dict, Any

# Your OKX API Credentials
API_KEY = "your_api_key"
API_SECRET = "your_secret_key"
PASSPHRASE = "your_passphrase"

# OKX Base URL
BASE_URL = "https://www.okx.com"


# Function to generate OKX signature
def generate_signature(
    timestamp: str, method: str, request_path: str, body: str = ""
) -> str:
    """Creates an HMAC-SHA256 signature for OKX API requests."""
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(API_SECRET.encode(), message.encode(), digestmod="sha256")
    return base64.b64encode(mac.digest()).decode()


# Function to make authenticated OKX API request
def okx_request(
    method: str, endpoint: str, params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Sends an authenticated request to OKX API."""
    timestamp = str(time.time())
    request_path = f"/api/v5{endpoint}"
    # Convert params to JSON if needed
    body = json.dumps(params) if params else ""
    # Generate signature
    signature = generate_signature(timestamp, method, request_path, body)
    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
    }
    url = BASE_URL + request_path
    response = requests.request(method, url, headers=headers, data=body)
    return response.json()
