import asyncio
import sys

import ccxt.pro as ccxt
from crypto_pandas.ccxt.async_ccxt_pandas_exchange import AsyncCCXTPandasExchange
from tests.test_ccxt_pandas_wrapper import settings

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    exchange = AsyncCCXTPandasExchange(exchange=ccxt.binance(settings))
    data = await exchange.load_cached_markets()
    order_book = await exchange.fetch_order_book(symbol="BTC/USDT:USDT")
    bids_asks = await exchange.fetch_bids_asks(
        symbols=["BTC/USDT:USDT", "ETH/USDT:USDT"]
    )
    trades = await exchange.fetch_trades(symbol="BTC/USDT")
    order = trades.query("side == 'buy'").tail(1)[["symbol", "price", "side"]]
    order["price"] /= 4
    order["notional"] = 110
    order["type"] = "limit"
    await exchange.close()
    response = await exchange.create_order(**order.to_dict("records")[0])
    cancel_response = await exchange.cancel_order(
        id=response["id"], symbol=response["symbol"]
    )
    await exchange.close()
    print(data)
    print(order_book)
    print(bids_asks.dropna(how="all", axis=1))
    print(trades)
    print(response)
    print(cancel_response)


if __name__ == "__main__":
    asyncio.run(main())
