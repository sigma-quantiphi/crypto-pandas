## v0.12.1
- Replaced Na values inside of markets limits with 0 for min and np.inf for max.

## v0.12.0
- Breaking Change: Replaced `notional` argument when sending orders with `cost` to align with CCXT.
- Added checks for order cost within bounds.

## v0.11.9
- Fix `orders_to_dict` should there be no price column.
- Added order create, cancel, edit methods that use websockets.

## v0.11.8
- Fixed order preprocessing for orders out of bounds.

## v0.11.7
- Added `fetch_my_dust_trades`, `fetch_portfolios`, `fetch_portfolio_details`, `fetch_accounts`.

## v0.11.6
- Added `fetch_orders_by_ids`, `fetch_orders_by_status`.

## v0.11.5
- Added multiple watch methods parsing: balance, my_liquidations, funding_rate.

## v0.11.4
- Added `lastTradeTimestamp` and `lastUpdateTimestamp` to datetime columns.

## v0.11.2
- Forward `close` as well into `AsyncCCXTPandasExchange`.

## v0.11.1
- Added `fetch_deposits_withdrawals`, `fetch_order_trades` and `fetch_volatility_history` methods.

## v0.11.0
- Refactored `preprocess_data` as method of CCXTProcessor and not CCXTPandasExchange.
- Introduced a type-hinting generator and used the created classes to introduce type-hinting.

## v0.10.4
- Migrated `fetch_deposit_withdraw_fees` to `currencies` format.

## v0.10.3
- Separate dataframe format for `fetch_currencies`.
- Switched `fetched_leverages` from standard to markets dataframe format.

## v0.10.2
- Improved performance by dropping Na before type conversion.

## v0.10.1
- Quick fix dict values params `|` changed to `or`

## v0.10.0
- Delegated price/amount rounding to ccxt.exchange.price_to_precision/amount_to_precision .
- Removal of price/amount rounding strategy.

## v0.9.32
- Remove error message on missing `amount` orders. Allows compatible with params={"cost": value}.
- Created fix using `reindex` should precision/ limit fields not exist in markets data.

## v0.9.32
- Enabled cost -> amount calculation for market orders.
- Created fix using `reindex` should precision/ limit fields not exist in markets data.

## v0.9.31
- Only adding `timestamp` and `datetime` fields to balance dataframe when present in dict.
- Only parsing numeric/bool/datetime fields if list non empty.

## v0.9.29
- Added `nextFundingDatetime` to datetime parsing.

## v0.9.28
- Only concat non empty orderbooks.

## v0.9.27
- Added `fundingRate` and `estimatedSettlePrice` to numeric fields.
- Introduced `dropna_fields` with default True to automatically remove all Na columns. 

## v0.9.26
- Addition of `fetch_cross_borrow_rate(s)` parsing.

## v0.9.25
- Addition of `fetch_all_greeks` parsing.

## v0.9.24
- Addition of `fetch_funding_rate` parsing.

## v0.9.23
- Add `return_exceptions` to lists of lists in async_concat_results.

## v0.9.22
- Print warnings for out of bounds orders only if dataframe not empty.
- Extract exchange name from exchange class if not provided.
- Certain tests reverted to prod Binance exchange.

## v0.9.20
- Added fields to numeric and numeric_datetime columns for parsing: fee, expiryDate, createdDate.

## v0.9.19
- Added parsing for `fetchLastPrices`, `fetchIsolatedBorrowRates` and `fetchIsolatedBorrowRate`.

## v0.9.18
- Added parsing for `fetchMarkets`, `fetchMarkPrices` and `fetchMarkPrice`.

## v0.9.15
- Added `price_out_of_range` and `volume_out_of_range` parameters to allow user
to determine if they want a warning when price/volume out of limits range or if they want the values to be clipped.

## v0.9.14
- Clipping `price` and `amount` only if min/max values are not null from `load_markets`.

## v0.9.11
- Added DataFrame parsing for `fetch_order_books`.

## v0.9.7
- Fix to `account` column name.

## v0.9.6
- `async_concat_results` can now accept awaitable, listvawaitable or listvlistvawaitable

## v0.9.5
- Introduced `account` and `exchange` parameters in BaseProcessor for Crypto-Pandas-Pro.
- Made `BaseProcessor` attribute of CCXTPandasExchange.

## v0.9.1
- Created asyncio `concat_gather_results` function.

## v0.9.0
- New architecture with simple method inheritance.
- Fixed `watchOHLCVForSymbols` data parsing.
- Fixed `ohlcv` snake/camel case mapping.
- Reintroduced semaphore.

## v0.8.0c
- Remove OHLCV symbol column. Async reroutes non async compatible methods.

## v0.8.0b
- Add `fundingHistory` data parsing

## v0.8.0a
- Both sync and async methods with getattr for simpler architecture and future method additions.
- Async create/edit/cancel orders now possible.

## v0.7.12
- Added fix should params column be provided.

## v0.7.11
- Fix to `fetch_funding_rates` dataframe output.

## v0.7.9
- Introduced `fetch_trading_fee` and `fetch_trading_fees`.

## v0.7.7
- Fix to rounding should `precision` or `limits` not be present in order creation/ editing.

## v0.7.5
- Keep None since.

## v0.7.4
- `since` can now be a str of pdTimedelta
e.g: `"7d"` to set 7 days ago.

## v0.7.2
- `since` can now be a dict of pd.DateOffset parameters
e.g: `{"days": -1, "hour": 0, "minute": 0, "seconds": 0}` to set  to yesterday midnight.

## v0.7.0
- Use underscore rather than dot for unpacking dict columns.

## v0.6.3
- Added balance parsing for isolated margins.

## v0.6.2
- Append `symbol` column to OHLCV to facilitate multi symbols.

## v0.6.0
- Both CCXTPandasExchange and AsyncCCXTPandasExchange no longer inherit from CCXT Exchange.

## v0.5.2
- Fixed `fetch_funding_history` API call in both sync and async class.

## v0.5.0
- Transformed `orders_dataframe_preprocessing` into standard function to allow simpler use within crypto-pandas-pro.

## v0.4.11
- Adding default `WindowsSelectorEventLoopPolicy` to `AsyncCCXTPandasExchange`.

## v0.4.10
- Added `fetch_funding_history` method.

## v0.4.5
- Set default errors to ignore.

## v0.4.0
- Introduced `CCXTPandasExchange` and `AsyncCCXTPandasExchange` to enable working with
`Pandas` in one line of code.

## v0.2.0
- New architecture around classes for Preprocessors.

## v0.1.20
- Added `market_to_dataframe()`

## v0.1.0

- Initial deploy