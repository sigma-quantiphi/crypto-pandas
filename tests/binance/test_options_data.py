import pandas as pd
from dotenv import dotenv_values

from crypto_pandas.binance.options.options_client import BinanceOptionsClient

today = pd.Timestamp.now()
tomorrow = today.ceil("1d")
config = dotenv_values("../../.env")
client = BinanceOptionsClient(
    api_key=config["BINANCE_KEY"], secret=config["BINANCE_SECRET"]
)
data = client.get_server_time()
print(data)
data = client.get_24hr_ticker_price_change_statistics()
print(data)
data = client.get_exchange_info()
print(data)
symbol = data["symbol"][0]
underlying = data["underlying"][0]
data = client.get_historical_exercise_records()
print(data)
data = client.get_open_interest(underlyingAsset="BTC", expiration=tomorrow)
print(data)
data = client.get_order_book(symbol=symbol)
print(data)
data = client.get_recent_trades_list(symbol=symbol)
print(data)
data = client.get_recent_trades_list(symbol=symbol)
print(data)
data = client.get_recent_block_trades()
print(data)
data = client.get_symbol_price_ticker(underlying=underlying)
print(data)
data = client.get_klines(symbol=symbol, interval="1h")
print(data)
data = client.get_historical_trades(symbol=symbol)
print(data)
data = client.get_mark()
print(data)
data = client.get_account_info()
print(data)
data = client.get_account_funding_flow()
print(data)
# data = client.get_download_id_for_option_transaction_history(
#     startTime=today - pd.DateOffset(days=10), endTime=today
# )
# print(data)
# downloadId = data["downloadId"]
# data = client.get_option_transaction_history_download_link_by_id(downloadId=downloadId)
# print(data)
data = client.get_option_order_history(symbol=symbol)
print(data)
data = client.get_current_open_option_orders()
print(data)
data = client.get_position()
print(data)
data = client.get_exercise_record()
print(data)
data = client.get_account_trade_list()
print(data)
print(client.used_weight_1m)
