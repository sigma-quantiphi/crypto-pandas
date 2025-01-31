import time
import hashlib
import hmac
import base64
import requests
import urllib.parse

# Your Kraken API Keys
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

# Kraken API Base URL
BASE_URL = "https://api.kraken.com"


# Generate a nonce (unique identifier for each request)
def get_nonce():
    return int(time.time() * 1000)


# Generate HMAC-SHA512 signature
def sign_request(uri_path, data):
    """Signs API request using HMAC-SHA512"""
    post_data = urllib.parse.urlencode(data)
    encoded = (str(data["nonce"]) + post_data).encode()
    message = uri_path.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(API_SECRET), message, hashlib.sha512)
    sig_digest = base64.b64encode(mac.digest())
    return sig_digest.decode()


# Make an authenticated request
def kraken_request(uri_path, data):
    """Sends an authenticated request to Kraken API"""
    headers = {
        "API-Key": API_KEY,
        "API-Sign": sign_request(uri_path, data),
    }
    response = requests.post(BASE_URL + uri_path, headers=headers, data=data)
    return response.json()
