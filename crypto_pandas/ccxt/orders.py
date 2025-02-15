import ccxt
import pprint

# Initialize the Bybit exchange with options enabled.
exchange = ccxt.bybit(
    {
        "apiKey": "YOUR_API_KEY",
        "secret": "YOUR_API_SECRET",
        "enableRateLimit": True,
        "options": {
            "defaultType": "option",  # Use the options API endpoints
        },
    }
)

# Optional: Use sandbox/testnet mode if available
exchange.set_sandbox_mode(True)

# Define the batch orders payload.
# According to Bybit v5 Options API, the endpoint expects a 'batchOrders' key
# containing a list of orders.
batch_params = {
    "batchOrders": [
        {
            "symbol": "BTC-210625C50000",  # Example option symbol; adjust to your instrument format.
            "side": "Buy",  # Buy side only
            "orderType": "Limit",  # Limit order type
            "qty": 1,  # Order quantity
            "price": 0.1,  # Limit price
            "timeInForce": "GoodTillCancel",  # Time in force
        },
        {
            "symbol": "ETH-210625P2000",
            "side": "Buy",
            "orderType": "Limit",
            "qty": 2,
            "price": 0.05,
            "timeInForce": "GoodTillCancel",
        },
    ]
}

# Place the batch orders using the appropriate v5 endpoint.
# In ccxt, this might be exposed as the method below (depending on your ccxt version).
try:
    response = exchange.private_post_v5_order_create_batch(batch_params)
    pprint.pprint(response)
except Exception as e:
    print("Error placing batch orders:", e)
