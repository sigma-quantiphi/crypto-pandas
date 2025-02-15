from crypto_pandas.binance.options.options_client import BinanceOptionsClient

client = BinanceOptionsClient()
trades = client.get_exchange_info()
data = client.get_server_time()
print(data)
