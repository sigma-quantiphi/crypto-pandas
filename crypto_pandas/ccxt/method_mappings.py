from crypto_pandas.utils.utils import add_camel_case_methods

standard_dataframe_methods = {
    "fetch_accounts",
    "fetch_portfolio_details",
    "fetch_portfolios",
    "cancel_all_orders",
    "cancel_all_orders_ws",
    "cancel_orders",
    "cancel_orders_ws",
    "cancel_orders_for_symbols",
    "create_orders",
    "create_orders_ws",
    "edit_orders",
    "edit_orders_ws",
    "fetch_borrow_interest",
    "fetch_borrow_rate_histories",
    "fetch_borrow_rate_history",
    "fetch_convert_trade_history",
    "fetch_cross_borrow_rates",
    "fetch_deposit_addresses",
    "fetch_deposits",
    "fetch_deposits_withdrawals",
    "fetch_funding_history",
    "fetch_funding_rate_history",
    "fetch_ledger",
    "fetch_leverage_tiers",
    "fetch_liquidations",
    "fetch_long_short_ratio_history",
    "fetch_margin_adjustment_history",
    "fetch_margin_modes",
    "fetch_markets",
    "fetch_my_dust_trades",
    "fetch_my_liquidations",
    "fetch_my_trades",
    "fetch_open_interest_history",
    "fetch_order_trades",
    "fetch_position_history",
    "fetch_positions",
    "fetch_positions_history",
    "fetch_positions_risk",
    "fetch_settlement_history",
    "fetch_trades",
    "fetch_transaction_fees",
    "fetch_transfers",
    "fetch_volatility_history",
    "fetch_withdrawals",
    "watch_liquidations",
    "watch_liquidations_for_symbols",
    "watch_my_liquidations",
    "watch_my_liquidations_for_symbols",
    "watch_my_trades",
    "watch_my_trades_for_symbols",
    "watch_positions",
    "watch_trades",
    "watch_trades_for_symbols",
}
markets_dataframe_methods = {
    "fetch_all_greeks",
    "fetch_bids_asks",
    "fetch_convert_currencies",
    "fetch_funding_rates",
    "fetch_isolated_borrow_rates",
    "fetch_last_prices",
    "fetch_leverages",
    "fetch_mark_prices",
    "fetch_tickers",
    "fetch_trading_fees",
    "load_markets",
    "watch_bids_asks",
    "watch_funding_rates",
    "watch_mark_prices",
    "watch_tickers",
}
currencies_dataframe_methods = {"fetch_currencies", "fetch_deposit_withdraw_fees"}
balance_dataframe_methods = {"fetch_balance", "watch_balance"}
ohlcv_dataframe_methods = {"fetch_ohlcv", "fetchOHLCV", "watch_ohlcv", "watchOHLCV"}
ohlcv_symbols_dataframe_methods = {"watch_ohlcv_for_symbols", "watchOHLCVForSymbols"}
orderbook_dataframe_methods = {
    "fetch_order_book",
    "watch_order_book",
    "watch_order_book_for_symbols",
}
orderbooks_dataframe_methods = {"fetch_order_books"}
orders_dataframe_methods = {
    "fetch_canceled_and_closed_orders",
    "fetch_canceled_orders",
    "fetch_closed_orders",
    "fetch_open_orders",
    "fetch_orders",
    "fetch_orders_by_ids",
    "fetch_orders_by_status",
    "fetch_orders_classic" "fetch_orders_ws",
    "watch_orders",
    "watch_orders_for_symbols",
}
dict_methods = {
    "cancel_order",
    "cancel_order_ws",
    "create_order",
    "create_order_ws",
    "edit_order",
    "edit_order_ws",
    "fetch_cross_borrow_rate",
    "fetch_deposit",
    "fetch_funding_rate",
    "fetch_greeks",
    "fetch_isolated_borrow_rate",
    "fetch_mark_price",
    "fetch_open_interest",
    "fetch_option",
    "fetch_option_chain",
    "fetch_option_positions",
    "fetch_order",
    "fetch_position",
    "fetch_status",
    "fetch_ticker",
    "fetch_trade",
    "fetch_trading_fee",
    "fetch_deposit_withdraw_fee",
    "watch_funding_rate",
    "watch_mark_price",
    "watch_position",
    "watch_ticker",
}
single_order_methods = {
    "create_order",
    "edit_order",
    "create_order_ws",
    "edit_order_ws",
}
bulk_order_methods = {
    "create_orders",
    "edit_orders",
    "create_orders_ws",
    "edit_orders_ws",
}
symbol_order_methods = {"cancel_orders_for_symbols"}
standard_dataframe_methods = add_camel_case_methods(standard_dataframe_methods)
markets_dataframe_methods = add_camel_case_methods(markets_dataframe_methods)
currencies_dataframe_methods = add_camel_case_methods(currencies_dataframe_methods)
balance_dataframe_methods = add_camel_case_methods(balance_dataframe_methods)
orderbook_dataframe_methods = add_camel_case_methods(orderbook_dataframe_methods)
orderbooks_dataframe_methods = add_camel_case_methods(orderbooks_dataframe_methods)
orders_dataframe_methods = add_camel_case_methods(orders_dataframe_methods)
dict_methods = add_camel_case_methods(dict_methods)
single_order_methods = add_camel_case_methods(single_order_methods)
bulk_order_methods = add_camel_case_methods(bulk_order_methods)
symbol_order_methods = add_camel_case_methods(symbol_order_methods)
dataframe_methods = (
    standard_dataframe_methods
    | markets_dataframe_methods
    | currencies_dataframe_methods
    | balance_dataframe_methods
    | ohlcv_dataframe_methods
    | ohlcv_symbols_dataframe_methods
    | orderbook_dataframe_methods
    | orders_dataframe_methods
)
modified_methods = dataframe_methods | dict_methods
