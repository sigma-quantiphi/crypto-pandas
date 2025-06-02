Examples
========

Synchronous usage
-----------------

.. code-block:: python

   import ccxt
   from crypto_pandas import CCXTPandasExchange

   binance = CCXTPandasExchange(exchange=ccxt.binance())
   df = binance.fetch_ohlcv("BTC/USDT", timeframe="1h", limit=1000)
   print(df.tail())

.. code-block:: text

                      open      high       low     close     volume
   timestamp
   2025-05-31 20:00  68216  68344.0  68112.0  68297.0   149.07
   2025-05-31 21:00  68297  68425.0  68205.0  68390.0   172.88
   2025-05-31 22:00  68390  68510.0  68334.0  68480.0   198.44
   2025-05-31 23:00  68480  68655.0  68412.0  68620.0   210.66
   2025-06-01 00:00  68620  68733.0  68545.0  68695.0   190.55

Asynchronous usage
------------------

.. code-block:: python

   import asyncio
   import ccxt.pro as ccxt
   from crypto_pandas import AsyncCCXTPandasExchange

   exchange = AsyncCCXTPandasExchange(ccxt.binance())

   async def main():
       df = await exchange.fetch_ohlcv("BTC/USDT", timeframe="1m", limit=500)
       print(df.tail())
       exchange.close()

   asyncio.run(main())

.. code-block:: text

                      open     high      low    close   volume
   timestamp
   2025-06-01 00:04  68670  68690.0  68654.0  68685.0   3.119
   2025-06-01 00:05  68685  68702.0  68660.0  68674.0   2.742
   2025-06-01 00:06  68674  68698.0  68650.0  68697.0   3.588
   2025-06-01 00:07  68697  68725.0  68690.0  68720.0   3.012
   2025-06-01 00:08  68720  68744.0  68705.0  68730.0   2.994