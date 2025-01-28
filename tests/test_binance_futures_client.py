from crypto_pandas.binance.binance_futures_client import BinanceFuturesClient

client = BinanceFuturesClient()
trades = client.get_fapi_klines(symbol="BTCUSDT", interval="8h")
print(trades)
