from crypto_pandas.bybit.bybit_client import BybitClient

client = BybitClient(
    env="prod",
)
trades = client.get_market_kline(
    symbol="BTCUSDT",
    interval=1,
)
print(trades)
trades = client.get_market_mark_price_kline(
    symbol="BTCUSDT",
    interval=1,
)
print(trades)
trades = client.get_market_index_price_kline(
    symbol="BTCUSDT",
    interval=1,
)
print(trades)
trades = client.get_market_orderbook(category="spot", symbol="BTCUSDT")
print(trades)
trades = client.get_market_tickers(category="linear", symbol="BTCPERP")
print(trades)
trades = client.get_market_funding_history(category="linear", symbol="BTCPERP")
print(trades)
trades = client.get_account_wallet_balance(accountType="UNIFIED")
print(trades)
