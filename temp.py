import ccxt
import pprint

from dotenv import dotenv_values

# Initialize the Bybit exchange with options enabled.
config = dotenv_values(".env")
exchange = ccxt.bybit(
    {
        "apiKey": config["BYBIT_KEY"],
        "secret": config["BYBIT_SECRET"],
        "options": {
            "defaultType": "option",  # Use the options API endpoints
        },
    }
)

# Optional: Use sandbox/testnet mode if available
exchange.set_sandbox_mode(True)

# Define the batch orders payload.
batch_params = {
    "batchOrders": [
        {
            "symbol": "BTC-160225C89000",  # Example option symbol; adjust to your instrument format.
            "side": "Buy",  # Buy side only
            "orderType": "Limit",  # Limit order type
            "qty": 0.01,  # Order quantity
            "price": 0.1,  # Limit price
            "timeInForce": "GoodTillCancel",  # Time in force
        },
    ]
}

try:
    response = exchange.private_post_v5_order_create_batch(batch_params)
    pprint.pprint(response)
except Exception as e:
    print("Error placing batch orders:", e)
