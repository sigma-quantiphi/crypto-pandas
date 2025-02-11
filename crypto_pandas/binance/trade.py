import pandas as pd


def account_to_dataframe(data: dict) -> pd.DataFrame:
    data = pd.json_normalize(
        data=data,
        meta=[
            "makerCommission",
            "takerCommission",
            "buyerCommission",
            "sellerCommission",
            ["commissionRates", "maker"],
            ["commissionRates", "taker"],
            ["commissionRates", "buyer"],
            ["commissionRates", "seller"],
            "canTrade",
            "canWithdraw",
            "canDeposit",
            "brokered",
            "requireSelfTradePrevention",
            "preventSor",
            "updateTime",
            "accountType",
            "permissions",
            "uid",
        ],
        record_path="balances",
    )
    return preprocess_dataframe(data)


def order_list_to_dataframe(data: dict) -> pd.DataFrame:
    data = pd.json_normalize(
        data=data,
        meta=[
            "orderListId",
            "contingencyType",
            "listStatusType",
            "listOrderStatus",
            "listClientOrderId",
            "transactionTime",
            "symbol",
            "isIsolated",
        ],
        record_path="orders",
    )
    return preprocess_dataframe(data)


def order_to_dataframe(data: dict) -> pd.DataFrame:
    data = pd.json_normalize(
        data=data,
        meta=[
            "symbol",
            "orderId",
            "orderListId",
            "clientOrderId",
            "transactTime",
            "price",
            "origQty",
            "executedQty",
            "origQuoteOrderQty",
            "cummulativeQuoteQty",
            "status",
            "timeInForce",
            "type",
            "side",
            "workingTime",
            "selfTradePreventionMode",
        ],
        record_path="fills",
        record_prefix="fills.",
    )
    return preprocess_dataframe(data)
