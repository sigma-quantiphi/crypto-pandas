import ccxt
import pprint

from dotenv import dotenv_values

# Initialize the Bybit exchange with options enabled.
config = dotenv_values("../../.env")
exchange = ccxt.bybit(
    {
        "apiKey": config["BYBIT_KEY"],
        "secret": config["BYBIT_SECRET"],
        "enableRateLimit": True,
    },
)

# Load all markets
markets = exchange.load_markets()

# markets = [m for m in markets if m.get("type") == "option"]
markets = markets.values()
print("\nFiltered Options Markets:")
for market in markets:
    print(market["id"])

# Optional: Use sandbox/testnet mode if available
# exchange.set_sandbox_mode(True)

# Define the batch orders payload.
batch_params = {
    "category": "option",
    "request": [
        {
            "symbol": "SOL-20FEB25-165-C",  # Example option symbol; adjust to your instrument format.
            "side": "Buy",  # Buy side only
            "orderType": "Limit",  # Limit order type
            "price": "0.01",  # Order quantity
            "qty": "1",  # Limit price
            "timeInForce": "GTC",  # Time in force
            "orderLinkId": "fsadaf",
        },
    ],
}
try:
    response = exchange.private_post_v5_order_create_batch(batch_params)
    pprint.pprint(response)
except Exception as e:
    print("Error placing batch orders:", e)
