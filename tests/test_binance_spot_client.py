from crypto_pandas.binance.binance_spot_client import BinanceSpotClient

api_key = ""
secret = ""

client = BinanceSpotClient(env="prod", api_key=api_key, secret=secret)
trades = client.get_api_depth(symbol="BTCUSDT")
print(trades)
trades = client.get_api_trades(symbol="BTCUSDT")
print(trades)
trades = client.get_api_historical_trades(symbol="BTCUSDT")
print(trades)
trades = client.get_api_agg_trades(symbol="BTCUSDT")
print(trades)
trades = client.get_api_klines(symbol="BTCUSDT", interval="8h")
print(trades)
trades = client.get_api_ui_klines(symbol="BTCUSDT", interval="8h")
print(trades)
trades = client.get_api_avg_price(symbol="BTCUSDT")
print(trades)
trades = client.get_api_ticker_24hr()
print(trades)
trades = client.get_sapi_v4_sub_account_assets(
    email=""
)
print(trades)
breakpoint()
