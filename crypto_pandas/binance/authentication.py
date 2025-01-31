import time
import requests
import urllib.parse

from crypto_pandas.hmac_authentication import generate_signature

# Your Binance API Credentials
API_KEY = "your_api_key"
API_SECRET = "your_secret_key"

# Binance API Base URL
BASE_URL = "https://api.binance.com"


# Function to make authenticated Binance API request
def binance_request(method, endpoint, params=None):
    """Sends an authenticated request to Binance API."""
    timestamp = int(time.time() * 1000)
    query_string = f"timestamp={timestamp}"
    if params:
        query_string += "&" + urllib.parse.urlencode(params)
    signature = generate_signature(API_SECRET, query_string)
    query_string += f"&signature={signature}"
    headers = {"X-MBX-APIKEY": API_KEY}
    url = f"{BASE_URL}{endpoint}?{query_string}"
    response = requests.request(method, url, headers=headers)
    return response.json()


# Example: Get Account Balance (Private API)
def get_account_balance():
    return binance_request("GET", "/api/v3/account")


# Run function
balance = get_account_balance()
print(balance)
