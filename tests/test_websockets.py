import asyncio
import sys

import ccxt.pro as ccxt
from crypto_pandas.ccxt.async_ccxt_pandas_exchange import AsyncCCXTPandasExchange

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    exchange = AsyncCCXTPandasExchange(exchange=ccxt.binance())
    n = 0
    data = await exchange.load_cached_markets()
    print(data)
    while n < 5:
        order_book = await exchange.watch_ohlcv(symbol="BTC/USDT:USDT")
        print(order_book)
        bids_asks = await exchange.watch_bids_asks(
            symbols=["BTC/USDT:USDT", "ETH/USDT:USDT"]
        )
        print(bids_asks.dropna(how="all", axis=1))
        trades = await exchange.watch_trades(symbol="BTC/USDT")
        print(trades)
        n += 1
    await exchange.close()


if __name__ == "__main__":
    asyncio.run(main())
