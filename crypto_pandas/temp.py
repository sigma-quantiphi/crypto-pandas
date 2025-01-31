from binance.client import Client

client = Client(API_KEY, API_SECRET)

# Example batch order
batch_orders = [
    {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "quantity": "0.001",
        "price": "40000",
        "timeInForce": "GTC",
    },
    {
        "symbol": "ETHUSDT",
        "side": "SELL",
        "type": "LIMIT",
        "quantity": "0.02",
        "price": "2500",
        "timeInForce": "GTC",
    },
]

# Send batch orders
response = client.create_batch_order(batch_orders)
print(response)
