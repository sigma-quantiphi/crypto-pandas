import asyncio
import time
import pandas as pd
import ccxt.pro as ccxt_pro
from crypto_pandas import AsyncCCXTPandasExchange

exchanges = ccxt_pro.exchanges
print("Number of exchanges: ", len(exchanges))

async def main():
    tasks = []
    close_tasks = []
    for exchange_name in exchanges:
        exchange_class = getattr(ccxt_pro, exchange_name)
        exchange = exchange_class({'enableRateLimit': True})
        pandas_exchange = AsyncCCXTPandasExchange(exchange=exchange)
        tasks.append(pandas_exchange.load_markets())
        close_tasks.append(exchange.close())
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    start_time = time.time()
    await asyncio.gather(*close_tasks, return_exceptions=True)
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    results = pd.concat(results)
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
