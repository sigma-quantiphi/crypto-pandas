def snake_to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def add_camel_case_methods(methods: set) -> set:
    new_set = set()
    for item in methods:
        new_set.add(item)
        new_set.add(snake_to_camel(item))
    return new_set


standard_dataframe_methods = {
    "cancel_orders",
    "cancel_all_orders",
    "create_orders",
    "cancel_orders_for_symbols",
    "edit_orders",
    "fetch_positions_risk",
    "fetch_positions",
    "fetch_positions_history",
    "fetch_position_history",
    "fetch_settlement_history",
    "fetch_transfers",
    "fetch_ledger",
    "fetch_withdrawals",
    "fetch_borrow_interest",
    "fetch_borrow_rate_histories",
    "fetch_borrow_rate_history",
    "fetch_funding_history",
    "fetch_funding_rate_history",
    "fetch_open_interest_history",
    "fetch_deposit_withdraw_fees",
    "fetch_transaction_fees",
    "fetch_deposits",
    "fetch_trades",
    "fetch_my_trades",
    "fetch_leverage_tiers",
    "fetch_leverages",
    "fetch_liquidations",
    "fetch_long_short_ratio_history",
    "fetch_margin_adjustment_history",
    "fetch_my_liquidations",
    "fetch_convert_trade_history",
    "watch_liquidations",
    "watch_liquidations_for_symbols",
    "watch_positions",
    "watch_my_trades",
    "watch_my_trades_for_symbols",
    "watch_trades",
    "watch_trades_for_symbols",
}
markets_dataframe_methods = {
    "load_markets",
    "fetch_trading_fees",
    "fetch_currencies",
    "fetch_tickers",
    "fetch_funding_rates",
    "fetch_bids_asks",
    "watch_bids_asks",
}
balance_dataframe_methods = {
    "fetch_balance",
}
ohlcv_dataframe_methods = {"fetch_ohlcv", "watch_ohlcv", "fetchOHLCV", "watchOHLCV"}
ohlcv_symbols_dataframe_methods = {"watch_ohlcv_for_symbols", "watchOHLCVForSymbols"}
orderbook_dataframe_methods = {
    "fetch_order_book",
    "watch_order_book",
    "watch_order_book_for_symbols",
}
orders_dataframe_methods = {
    "fetch_orders",
    "fetch_open_orders",
    "fetch_closed_orders",
    "fetch_canceled_and_closed_orders",
    "watch_orders",
    "watch_orders_for_symbols",
}
dict_methods = {
    "cancel_order",
    "create_order",
    "edit_order",
    "fetch_trade",
    "fetch_deposit",
    "fetch_trading_fee",
    "fetch_position",
    "fetch_ticker",
    "fetch_open_interest",
    "fetch_status",
    "fetch_greeks",
    "fetch_option",
    "fetch_order",
    "watch_ticker",
    "watch_position",
}
single_order_methods = {"create_order", "edit_order"}
bulk_order_methods = {"create_orders", "edit_orders"}
symbol_order_methods = {"cancel_orders_for_symbols"}
standard_dataframe_methods = add_camel_case_methods(standard_dataframe_methods)
markets_dataframe_methods = add_camel_case_methods(markets_dataframe_methods)
balance_dataframe_methods = add_camel_case_methods(balance_dataframe_methods)
orderbook_dataframe_methods = add_camel_case_methods(orderbook_dataframe_methods)
orders_dataframe_methods = add_camel_case_methods(orders_dataframe_methods)
dict_methods = add_camel_case_methods(dict_methods)
single_order_methods = add_camel_case_methods(single_order_methods)
bulk_order_methods = add_camel_case_methods(bulk_order_methods)
symbol_order_methods = add_camel_case_methods(symbol_order_methods)
dataframe_methods = (
    standard_dataframe_methods
    | markets_dataframe_methods
    | balance_dataframe_methods
    | ohlcv_dataframe_methods
    | orderbook_dataframe_methods
    | orders_dataframe_methods
)
