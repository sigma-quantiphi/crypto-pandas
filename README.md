# Crypto Pandas

![Python version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)
[![GitHub](https://img.shields.io/badge/github-Visit&nbsp;Repo-black?style=for-the-badge&logo=github)](https://github.com/sigma-quantiphi/crypto-pandas)
[![PyPI version](https://badge.fury.io/py/crypto-pandas.svg)](https://pypi.org/project/crypto-pandas/)
[![Downloads](https://img.shields.io/pypi/dm/crypto-pandas)](https://pypi.org/project/crypto-pandas/#files)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/sigma-quantiphi/crypto-pandas/HEAD?urlpath=%2Fdoc%2Ftree%2Fexamples)
[![Explore Data](https://img.shields.io/badge/Explore%20Data-CCXT--Explorer-ffffff?logo=streamlit&style=plastic&color=ffffff&logoColor=FF4B4B)](https://www.ccxt-explorer.com/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sigma-quantiphi/crypto-pandas/blob/main/LICENSE.md)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docs](https://readthedocs.org/projects/crypto-pandas/badge/?version=latest)](https://crypto-pandas.readthedocs.io/en/latest/)
[![Medium badge](https://img.shields.io/badge/-Follow&nbsp;on&nbsp;Medium-black?style=social&logo=medium)](https://medium.com/@lucasjamar47)

Crypto Pandas is a lightweight Python library that fuses the power of [pandas](https://pandas.pydata.org/) with the market-connectivity of [CCXT](https://github.com/ccxt/ccxt/).
In a single line, it transforms CCXT’s raw JSON into a clean, typed DataFrame, ready for analysis, back-testing, or real-time dashboards.
The same DataFrame-centric API also lets you create, edit, and cancel live exchange orders directly from pandas DataFrames.

## Features

- Transformation of outputs to pandas DataFrame when applicable.
- Setting proper data types.
- Transformation of DataFrame of orders to ensure proper format for exchange:
  - Determining volume based on notional amount if user prefers providing notional
  - Rounding and capping of price and volume based on exchange's symbol parameters.

## Installation

Crypto Pandas can be installed on Python 3.11~3.13:

```bash
pip install crypto-pandas
```

## Getting Started

Crypt -Pandas works near identically to CCXT. Just add `exchange = CCXTPandasExchange(exchange=exchange)`
and the exchange methods provided by CCXT will be exposed to Crypto Pandas.
More examples can be found on [Binder](https://mybinder.org/v2/gh/sigma-quantiphi/crypto-pandas/HEAD?urlpath=%2Fdoc%2Ftree%2Fexamples): 

```python
import ccxt
from crypto_pandas import CCXTPandasExchange

# Initialize a CCXTPandasExchange object
exchange = ccxt.binance(dict(apiKey="your_api_key_here", secret="your_secret_here"))
exchange = CCXTPandasExchange(exchange=exchange)

# Fetch open orders from an exchange
open_orders = exchange.fetch_open_orders(symbol="BTC/USDT")

# Halve the amount and edit orders
open_orders["amount"] /= 2
response = exchange.edit_orders(open_orders)

# Display the transformed orders dataframe
print(response)
```

## Documentation

For detailed documentation, visit the [ReadTheDocs](https://crypto-pandas.readthedocs.io/en/latest/) or read the API reference for
advanced features.

## About Sigma Quantiphi
[Sigma Quantiphi](https://www.sigmaquantiphi.com/) is a quantitative-engineering firm that builds end-to-end algorithmic-trading systems for the cryptocurrency markets.
We create open-source, Python-first tools—like crypto-pandas—and deliver turnkey execution, data, and research pipelines that emphasize simplicity, transparency, and rapid deployment.

## License

This project is licensed under the Apache License. See the `LICENSE` file for more details.

## Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository, create a new branch for your feature
or fix, and send a pull request.

1. Fork the repository.
2. Create your feature/fix branch: `git checkout -b my-new-feature`.
3. Commit your changes: `git commit -am 'Add some feature'`.
4. Push to the branch: `git push origin my-new-feature`.
5. Submit a pull request.

## Support

If you encounter any issues or have questions, feel free to open an issue on
the [GitHub repository](https://github.com/yourusername/crypto-pandas) or contact us via email at contact@sqphi.com.
Happy trading! 🚀
