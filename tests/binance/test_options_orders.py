from dotenv import dotenv_values

from crypto_pandas.binance.options_client import BinanceOptionsClient

config = dotenv_values(".env")
underlying = "BTCUSDT"
client = BinanceOptionsClient(
    api_key=config["BINANCE_KEY"], secret=config["BINANCE_SECRET"]
)
symbols = client.get_exchange_info()[
    [
        "expiryDate",
        "symbol",
        "side",
        "strikePrice",
        "underlying",
    ]
]
symbols = symbols.query("underlying == @underlying")
symbols = symbols.loc[symbols["expiryDate"] == symbols["expiryDate"].min()]
symbols = symbols.loc[
    (
        (symbols["side"] == "CALL")
        & (symbols["strikePrice"] == symbols["strikePrice"].min())
    )
    | (
        (symbols["side"] == "PUT")
        & (symbols["strikePrice"] == symbols["strikePrice"].max())
    )
]
symbols = symbols[["symbol"]]
symbols["side"] = "BUY"
symbols["quantity"] = 0.01
symbols["price"] = 5
symbols["timeInForce"] = "GTC"

response = client.send_batch_orders(orders=symbols)
print(response)
response = client.cancel_all_orders_by_underlying(underlying=underlying)
print(response)
breakpoint()
