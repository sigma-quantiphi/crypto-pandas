import ccxt
import ccxt.pro as ccxt_pro


def snake_to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def add_camel_case_methods(methods: set) -> set:
    new_set = set()
    for item in methods:
        new_set.add(item)
        new_set.add(snake_to_camel(item))
    return new_set


def exchange_has_method(exchange: ccxt.Exchange | ccxt_pro.Exchange, method: str) -> bool:
    """Checks if an exchange has a specific method"""
    method = snake_to_camel(method)
    return method in exchange.has and exchange.has[method] == True


if __name__ == "__main__":
    print(exchange_has_method(ccxt.binance(), "fetch_order_book"))
    print(exchange_has_method(ccxt_pro.binance(), "createOrderWs"))
    print(exchange_has_method(ccxt_pro.binance(), "create_order_ws"))
    print(exchange_has_method(ccxt_pro.binance(), "create_orders_Ws"))
