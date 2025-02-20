from typing import Union


def check_missing_element(
    required: set, values: list, message: str = "Order Type"
) -> None:
    missing_values = [x for x in required if x not in values]
    if any(missing_values):
        raise ValueError(f"{message}: {missing_values}")


def check_str_or_list_in_list(
    values: Union[str, list], possible_values: set, message: str = "Order Type"
) -> None:
    if isinstance(values, str):
        values = list(values)
    wrong_parameters = [item for item in values if not item in possible_values]
    if not wrong_parameters:
        raise ValueError(f"{message}: {wrong_parameters} is not one {possible_values}")


def check_missing_column(required: set, values: list) -> None:
    check_missing_element(required=required, values=values, message="Missing column")


def check_sides(order_sides: Union[str, list]) -> None:
    check_str_or_list_in_list(
        values=order_sides, possible_values={"BUY", "SELL"}, message="Side"
    )


def check_order_types(order_types: Union[str, list], possible_values: set) -> None:
    check_str_or_list_in_list(
        values=order_types, possible_values=possible_values, message="Order Type"
    )


def check_order_time_in_force(
    order_time_in_force: Union[str, list], possible_values: set
) -> None:
    check_str_or_list_in_list(
        values=order_time_in_force,
        possible_values=possible_values,
        message="Order Time In Force",
    )
