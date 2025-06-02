# Crypto Pandas

![Python version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)
[![PyPI version](https://badge.fury.io/py/crypto-pandas.svg)](https://pypi.org/project/crypto-pandas/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/sigma-quantiphi/crypto-pandas/HEAD?labpath=examples)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sigma-quantiphi/crypto-pandas/blob/main/LICENSE.md)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docs](https://readthedocs.org/projects/crypto-pandas/badge/?version=latest)](https://crypto-pandas.readthedocs.io/en/latest/)
[![Medium badge](https://img.shields.io/badge/-Follow&nbsp;on&nbsp;Medium-black?style=social&logo=medium)](https://medium.com/@lucasjamar47)

Crypto Pandas is a Python library that simplifies the process of interacting with cryptocurrency exchanges via the CCXT
library. It focuses on streamlining the process of fetching and cleaning exchange-related data, as well as transforming
dataframes of orders to send to the exchange.

## Features

- Simplified integration with the CCXT library.
- Utilities for cleaning and preparing exchange data.
- Easy transformation of order dataframes for compatibility with cryptocurrency exchanges.

## Installation

To install Crypto Pandas, you can use `pip`:

```bash
pip install crypto-pandas
```

Make sure you have Python 3.12+ installed. You can check your Python version by running:

```bash
python --version
```

If any dependencies are missing, they will be installed automatically.

## Getting Started

Here’s a quick example of how to use Crypto Pandas to fetch and clean data using CCXT.

### Basic Usage

Crypto-Pandas works near identically to CCXT. Just add `exchange = CCXTPandasExchange(exchange=exchange)`
and the exchange methods provided by CCXT will be exposed to Crypto-Pandas.

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
the [GitHub repository](https://github.com/yourusername/crypto-pandas) or contact us via email at
support@sqphi.com.
Happy trading! 🚀
