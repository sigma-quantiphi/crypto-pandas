import time
import hmac
import hashlib
import requests

# Your Coinbase API Credentials
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

# Coinbase API Base URL
BASE_URL = "https://api.coinbase.com"


# Function to generate HMAC-SHA256 signature
def generate_signature(timestamp, method, request_path, body=""):
    """Creates an HMAC-SHA256 signature for Coinbase API requests."""
    message = f"{timestamp}{method}{request_path}{body}"
    mac = hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256)
    return mac.hexdigest()


# Function to make authenticated Coinbase API request
def coinbase_request(method, endpoint, params=None):
    """Sends an authenticated request to Coinbase API."""
    timestamp = str(int(time.time()))
    request_path = f"/v2{endpoint}"
    body = params if params else ""
    # Generate signature
    signature = generate_signature(timestamp, method, request_path, body)
    headers = {
        "CB-ACCESS-KEY": API_KEY,
        "CB-ACCESS-SIGN": signature,
        "CB-ACCESS-TIMESTAMP": timestamp,
    }
    url = BASE_URL + request_path
    response = requests.request(method, url, headers=headers, json=params)
    return response.json()
