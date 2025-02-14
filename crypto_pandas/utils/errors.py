from typing import Union


def check_missing_element(required: list, values: list) -> None:
    missing_values = [x for x in required if x not in values]
    if any(missing_values):
        raise ValueError(f"Missing: {missing_values}")


def check_str_or_list_in_list(
    parameters: Union[str, list[str]], possible_values: set
) -> None:
    if isinstance(parameters, str):
        parameters = list(parameters)
    wrong_parameters = [item for item in parameters if not item in possible_values]
    if not wrong_parameters:
        raise ValueError(f"{wrong_parameters} are not one {possible_values}")


def check_number_in_range(
    parameters: Union[str, list[str]], possible_values: set
) -> None:
    if isinstance(parameters, str):
        parameters = list(parameters)
    wrong_parameters = [item for item in parameters if not item in possible_values]
    if not wrong_parameters:
        raise ValueError(f"{wrong_parameters} are not one {possible_values}")
