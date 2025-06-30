import asyncio
import ccxt.pro as ccxt_pro
from crypto_pandas import AsyncCCXTPandasExchange

exchange = ccxt_pro.binance()
pandas_exchange = AsyncCCXTPandasExchange(exchange=exchange)
symbols = ["BTC/USDT:USDT", "ETH/USDT:USDT"]
symbolsAndTimeframes = [[x, "1m"] for x in symbols]


async def main():
    try:
        while True:
            tasks = [
                pandas_exchange.watchOHLCVForSymbols(
                    symbolsAndTimeframes=symbolsAndTimeframes
                ),
                pandas_exchange.watchBidsAsks(symbols=symbols),
                pandas_exchange.watchTradesForSymbols(symbols=symbols),
                pandas_exchange.watchOrderBookForSymbols(symbols=symbols),
            ]
            ohlcv, bids_asks, trades, ob = await asyncio.gather(*tasks)
            await exchange.close()
            print("Received OHLCV")
            print(ohlcv)
            print("Received Bids Asks")
            print(bids_asks)
            print("Received Trades")
            print(trades)
            print("Received OB")
            print(ob)
    except KeyboardInterrupt:
        print("Websocket connection closed")
    finally:
        await exchange.close()


if __name__ == "__main__":
    asyncio.run(main())
