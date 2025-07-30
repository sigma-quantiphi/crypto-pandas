import asyncio
import ccxt.pro as ccxt_pro
import pandas as pd

from crypto_pandas import AsyncCCXTPandasExchange

exchange = ccxt_pro.binance()
pandas_exchange = AsyncCCXTPandasExchange(exchange=exchange)
symbols = ["BTC/USDT:USDT", "ETH/USDT:USDT"]
symbolsAndTimeframes = [[x, "1m"] for x in symbols]

results = {}


def tick():
    # sync point for all three coroutines
    # when one of these three streams is updated
    # it prints the last data from each of the three streams
    print(pd.Timestamp.now(tz="UTC"))
    print("=======================================================")
    print(results["ohlcv"])
    print(".......................................................")
    print(results["bids_asks"])
    print(".......................................................")
    print(results["trades"])
    print("=======================================================")
    print("\n\n\n")


async def run_ohlcv_loop():
    while True:
        try:
            results["ohlcv"] = await pandas_exchange.watchOHLCVForSymbols(
                symbolsAndTimeframes=symbolsAndTimeframes
            )
            tick()
        except Exception as e:
            print(type(e).__name__, str(e))
            break


async def run_bids_asks_loop():
    while True:
        try:
            results["bids_asks"] = await pandas_exchange.watchBidsAsks(symbols=symbols)
            tick()
        except Exception as e:
            print(type(e).__name__, str(e))
            break


async def run_trades_loop():
    while True:
        try:
            results["trades"] = await pandas_exchange.watchTradesForSymbols(
                symbols=symbols
            )
            tick()
        except Exception as e:
            print(type(e).__name__, str(e))
            break


async def main():
    try:
        tasks = [
            run_ohlcv_loop(),
            run_bids_asks_loop(),
            run_trades_loop(),
        ]
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("Websocket connection closed")
    finally:
        await exchange.close()


if __name__ == "__main__":
    asyncio.run(main())
