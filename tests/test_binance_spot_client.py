from crypto_pandas.binance.binance_spot_client import BinanceSpotClient

client = BinanceSpotClient()
trades = client.get_api_klines(symbol="BTCUSDT", interval="8h")
print(trades)
trades = client.get_api_ui_klines(symbol="BTCUSDT", interval="8h")
print(trades)
