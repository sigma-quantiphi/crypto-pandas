Examples
========

Synchronous usage
-----------------

.. code-block:: python

   import ccxt
   from crypto_pandas import CCXTPandasExchange

   exchange = ccxt.binance()
   pandas_exchange = CCXTPandasExchange(exchange=exchange)
   ohlcv = pandas_exchange.fetch_ohlcv("BNB/USDT", timeframe="1h", limit=1000)
   order_book = pandas_exchange.fetch_order_book("BNB/USDT", limit=1000)
   print(ohlcv.tail())
   print(order_book.tail())

.. code-block:: text

                        timestamp    open    high     low   close    volume
    995 2025-06-02 05:00:00+00:00  657.62  658.48  655.71  657.22  2922.537
    996 2025-06-02 06:00:00+00:00  657.23  658.88  656.30  657.84  4882.567
    997 2025-06-02 07:00:00+00:00  657.84  659.40  657.73  658.16  8241.973
    998 2025-06-02 08:00:00+00:00  658.16  658.57  655.36  655.83  4895.569
    999 2025-06-02 09:00:00+00:00  655.83  655.89  653.22  654.89  4198.651

           price    qty    symbol timestamp datetime        nonce  side
    1995  643.96  3.226  BNB/USDT       NaT      NaT  14090677334  bids
    1996  643.95  0.028  BNB/USDT       NaT      NaT  14090677334  bids
    1997  643.93  0.046  BNB/USDT       NaT      NaT  14090677334  bids
    1998  643.92  0.042  BNB/USDT       NaT      NaT  14090677334  bids
    1999  643.91  0.153  BNB/USDT       NaT      NaT  14090677334  bids

Asynchronous usage
------------------

.. code-block:: python

   import asyncio
   import ccxt.pro as ccxt
   from crypto_pandas import AsyncCCXTPandasExchange

   exchange = ccxt.binance()
   pandas_exchange = AsyncCCXTPandasExchange(exchange=exchange)

   async def main():
       ohlcv = await pandas_exchange.fetch_ohlcv("BNB/USDT", timeframe="1m", limit=500)
       order_book = await pandas_exchange.fetch_order_book("BNB/USDT", limit=500)
       print(ohlcv.tail())
       print(order_book.tail())
       exchange.close()

   asyncio.run(main())

.. code-block:: text

                        timestamp    open    high     low   close    volume
    995 2025-06-02 05:00:00+00:00  657.62  658.48  655.71  657.22  2922.537
    996 2025-06-02 06:00:00+00:00  657.23  658.88  656.30  657.84  4882.567
    997 2025-06-02 07:00:00+00:00  657.84  659.40  657.73  658.16  8241.973
    998 2025-06-02 08:00:00+00:00  658.16  658.57  655.36  655.83  4895.569
    999 2025-06-02 09:00:00+00:00  655.83  655.89  653.22  654.89  4198.651

           price    qty    symbol timestamp datetime        nonce  side
    1995  643.96  3.226  BNB/USDT       NaT      NaT  14090677334  bids
    1996  643.95  0.028  BNB/USDT       NaT      NaT  14090677334  bids
    1997  643.93  0.046  BNB/USDT       NaT      NaT  14090677334  bids
    1998  643.92  0.042  BNB/USDT       NaT      NaT  14090677334  bids
    1999  643.91  0.153  BNB/USDT       NaT      NaT  14090677334  bids


Websockets usage
----------------

.. code-block:: python

   import asyncio
   import ccxt.pro as ccxt

   async def main():
       exchange = ccxt.binance({
           "enableRateLimit": True,
       })
       pandas_exchange = AsyncCCXTPandasExchange(exchange=exchange)
       try:
           while True:
               ohlcv = await pandas_exchange.watch_ohlcv("BNB/USDT")
               order_book = await pandas_exchange.watch_order_book("BNB/USDT")
               print(ohlcv)
               print(order_book)
       except KeyboardInterrupt:
           print("Websocket connection closed")
       finally:
           await exchange.close()

   asyncio.run(main())
