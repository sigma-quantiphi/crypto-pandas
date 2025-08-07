import asyncio

import ccxt.pro as ccxt
from crypto_pandas.ccxt.async_ccxt_pandas_exchange import AsyncCCXTPandasExchange
from tests.test_sync import sandbox_settings


async def main():
    exchange = ccxt.binance(sandbox_settings)
    exchange.set_sandbox_mode(True)
    pandas_exchange = AsyncCCXTPandasExchange(exchange=exchange, max_number_of_orders=5)
    markets, order_book, bids_asks, trades = await asyncio.gather(
        pandas_exchange.load_cached_markets(),
        pandas_exchange.fetch_order_book(symbol="BNB/USDT:USDT"),
        pandas_exchange.fetch_bids_asks(
            symbols=["BNB/USDT:USDT", "DOGE/USDT:USDT", "XRP/USDT:USDT"]
        ),
        pandas_exchange.fetch_trades(symbol="BNB/USDT"),
        return_exceptions=True,
    )
    print(markets)
    print(order_book)
    print(bids_asks.dropna(how="all", axis=1))
    print(trades)
    orders = (
        bids_asks[["symbol", "bid"]]
        .drop_duplicates(subset=["symbol"], ignore_index=True)
        .rename(columns={"bid": "price"})
    )
    orders["side"] = "buy"
    orders["price"] /= 4
    orders["notional"] = 12
    orders["type"] = "limit"
    response = await pandas_exchange.create_orders(orders=orders)
    print(response)
    for symbol in response["symbol"]:
        cancel_response = await pandas_exchange.cancel_all_orders(symbol=symbol)
        print(cancel_response)
    await exchange.close()


if __name__ == "__main__":
    asyncio.run(main())
