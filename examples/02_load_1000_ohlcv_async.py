import asyncio
import time
import pandas as pd
import ccxt.pro as ccxt_pro
from crypto_pandas import AsyncCCXTPandasExchange

exchange = ccxt_pro.binance()
pandas_exchange = AsyncCCXTPandasExchange(exchange=exchange)


async def main():
    symbols = await pandas_exchange.load_markets()
    symbols = symbols.head(1000)
    print(symbols[["symbol", "base", "quote"]])
    tasks = []
    for symbol in symbols["symbol"]:
        tasks.append(
            pandas_exchange.fetch_ohlcv(symbol=symbol, timeframe="1m", limit=1000)
        )
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    await exchange.close()
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    results = pd.concat(results)
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
