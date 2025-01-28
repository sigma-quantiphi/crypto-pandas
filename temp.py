from pybit.unified_trading import HTTP

session = HTTP(
    testnet=False,
    api_key="...",
    api_secret="...",
)

# Create five long USDC Options orders.
# (Currently, only USDC Options support sending orders in bulk.)
payload = {"category": "option"}
orders = [{
  "symbol": "BTC-30JUN23-20000-C",
  "side": "Buy",
  "orderType": "Limit",
  "qty": "0.1",
  "price": i,
} for i in [15000, 15500, 16000, 16500, 16600]]

payload["request"] = orders
# Submit the orders in bulk.
session.place_batch_order(payload)