import asyncio

import ccxt.pro as ccxt
from crypto_pandas.ccxt.async_ccxt_pandas_exchange import AsyncCCXTPandasExchange


async def main():
    exchange = AsyncCCXTPandasExchange(exchange=ccxt.binance())
    n = 0
    data = await exchange.load_cached_markets()
    print(data)
    while n < 5:
        tasks = (
            exchange.watch_ohlcv(symbol="BTC/USDT:USDT"),
            exchange.watch_bids_asks(symbols=["BTC/USDT:USDT", "ETH/USDT:USDT"]),
            exchange.watch_trades(symbol="BTC/USDT:USDT"),
        )
        order_book, bids_asks, trades = await asyncio.gather(*tasks)
        print(order_book)
        print(bids_asks.dropna(how="all", axis=1))
        print(trades)
        n += 1
    await exchange.close()


if __name__ == "__main__":
    asyncio.run(main())
