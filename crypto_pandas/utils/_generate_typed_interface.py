import inspect
from typing import Callable
import ccxt
import ccxt.pro as ccxt_pro

from crypto_pandas.ccxt.method_mappings import dataframe_methods, modified_methods

types_dict = {
    "Literal['buy', 'sell']": "OrderSide",
    "Literal['limit', 'market']": "OrderType",
    "Literal['long', 'short']": "PositionSide",
    "Union[str, int]": "IndexType",
    "Union[None, str, float, int, decimal.Decimal]": "Num",
    "Optional[str]": "Str",
    "Optional[List[str]]": "Strings",
    "Optional[int]": "Int",
    "Optional[bool]": "Bool",
    "Literal['spot', 'margin', 'swap', 'future', 'option']": "MarketType",
    "Literal['linear', 'inverse']": "SubType",
}


def get_signature_with_custom_types(method: Callable, method_name: str) -> str:
    sig = inspect.signature(method)
    params = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        param_str = name
        if param.annotation != inspect.Parameter.empty:
            annotation = str(param.annotation)
            if (
                "typing." in annotation
                or "ccxt.base.types." in annotation
                or "decimal." in annotation
            ):
                annotation = (
                    annotation.replace("typing.", "")
                    .replace("ccxt.base.types.", "")
                    .replace("decimal.", "")
                )
                if annotation in types_dict:
                    annotation = types_dict[annotation]
            elif hasattr(param.annotation, "__name__"):
                annotation = param.annotation.__name__
            if name == "since":
                annotation = "int | pd.Timestamp | dict | str | None"
            elif name == "orders":
                annotation = "pd.DataFrame"
            param_str += f": {annotation}"
        if param.default is not inspect.Parameter.empty:
            param_str += f" = {param.default!r}"
        params.append(param_str)
    param_str = ", ".join(["self"] + params)
    return_type = "pd.DataFrame" if method_name in dataframe_methods else "dict"
    return f'''
    def {method_name}({param_str}) -> {return_type}:
        """Returns a {return_type} from ccxt.{method_name}"""
        ...'''


def generate_typed_interface_class(base: type, class_name: str) -> str:
    import_lines = """from decimal import Decimal
from types import NoneType
from typing import List, Union, Protocol
from ccxt.base.types import Int, OrderSide, OrderType, Str, Strings
import pandas as pd\n\n
"""
    class_header = f'''class {class_name}(Protocol):
    """A Class to add type hinting to {class_name}"""
'''
    lines = []
    for method_name in modified_methods:
        if hasattr(base, method_name):
            method = getattr(base, method_name)
            try:
                stub = get_signature_with_custom_types(method, method_name)
                lines.append(stub)
            except Exception as e:
                print(f"Error inspecting {method_name}: {e}")
    return import_lines + class_header + "\n".join(lines)


if __name__ == "__main__":
    sync_code = generate_typed_interface_class(ccxt.Exchange, "CCXTPandasExchangeTyped")
    async_code = generate_typed_interface_class(
        ccxt_pro.Exchange, "AsyncCCXTPandasExchangeTyped"
    )
    with open("crypto_pandas/utils/ccxt_pandas_exchange_typed.py", "w") as f:
        f.write(sync_code)
    with open("crypto_pandas/utils/async_ccxt_pandas_exchange_typed.py", "w") as f:
        f.write(async_code)
    print("Generated both typed interface files.")
