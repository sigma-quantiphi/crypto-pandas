## [0.9.7]
* Fix to `account` column name.

## [0.9.6]
* `async_concat_results` can now accept awaitable, list[awaitable] or list[list[awaitable]]

## [0.9.5]
* Introduced `account` and `exchange` parameters in BaseProcessor for Crypto-Pandas-Pro.
* Made `BaseProcessor` attribute of CCXTPandasExchange.

## [0.9.1]
* Created asyncio `concat_gather_results` function.

## [0.9.0]
* New architecture with simple method inheritance.
* Fixed `watchOHLCVForSymbols` data parsing.
* Fixed `ohlcv` snake/camel case mapping.
* Reintroduced semaphore.

## [0.8.0c]
* Remove OHLCV symbol column. Async reroutes non async compatible methods.

## [0.8.0b]
* Add `fundingHistory` data parsing

## [0.8.0a]
* Both sync and async methods with getattr for simpler architecture and future method additions.
* Async create/edit/cancel orders now possible.

## [0.7.12]
* Added fix should params column be provided.

## [0.7.11]
* Fix to `fetch_funding_rates` dataframe output.

## [0.7.9]
* Introduced `fetch_trading_fee` and `fetch_trading_fees`.

## [0.7.7]
* Fix to rounding should `precision` or `limits` not be present in order creation/ editing.

## [0.7.5]
* Keep None since.

## [0.7.4]
* `since` can now be a str of pdTimedelta
e.g: `"7d"` to set 7 days ago.

## [0.7.2]
* `since` can now be a dict of pd.DateOffset parameters
e.g: `{"days": -1, "hour": 0, "minute": 0, "seconds": 0}` to set  to yesterday midnight.

## [0.7.0]
* Use underscore rather than dot for unpacking dict columns.

## [0.6.3]
* Added balance parsing for isolated margins.

## [0.6.2]
* Append `symbol` column to OHLCV to facilitate multi symbols.

## [0.6.0]
* Both CCXTPandasExchange and AsyncCCXTPandasExchange no longer inherit from CCXT Exchange.

## [0.5.2]
* Fixed `fetch_funding_history` API call in both sync and async class.

## [0.5.0]
* Transformed `orders_dataframe_preprocessing` into standard function to allow simpler use within crypto-pandas-pro.

## [0.4.11]
* Adding default `WindowsSelectorEventLoopPolicy` to `AsyncCCXTPandasExchange`.

## [0.4.10]
* Added `fetch_funding_history` method.

## [0.4.5]
* Set default errors to ignore.

## [0.4.0]
* Introduced `CCXTPandasExchange` and `AsyncCCXTPandasExchange` to enable working with
`Pandas` in one line of code.

## [0.2.0]
* New architecture around classes for Preprocessors.

## [0.1.20]
* Added `market_to_dataframe()`

## [0.1.0] - 2025-01-27

Initial deploy