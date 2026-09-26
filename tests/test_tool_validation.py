from app.tools.validator import (
    extract_known_values,
    validate_tool_arguments,
)


def test_extract_price_and_cost():
    messages = [
        {
            "role": "user",
            "content": (
                "Цена товара 1500 рублей, "
                "себестоимость 600 рублей."
            ),
        }
    ]

    values = extract_known_values(messages)

    assert values["price"] == 1500
    assert values["cost"] == 600


def test_tool_arguments_match_user_data():
    messages = [
        {
            "role": "user",
            "content": (
                "Цена товара 1500 рублей, "
                "себестоимость 600 рублей."
            ),
        }
    ]

    valid, error = validate_tool_arguments(
        tool_name="calculate_margin",
        arguments={
            "price": 1500,
            "cost": 600,
        },
        messages=messages,
    )

    assert valid is True
    assert error is None


def test_hallucinated_cost_is_rejected():
    messages = [
        {
            "role": "user",
            "content": "Цена товара 1500 рублей.",
        }
    ]

    valid, error = validate_tool_arguments(
        tool_name="calculate_margin",
        arguments={
            "price": 1500,
            "cost": 1000,
        },
        messages=messages,
    )

    assert valid is False
    assert error is not None


def test_wrong_cost_is_rejected():
    messages = [
        {
            "role": "user",
            "content": (
                "Цена товара 1500 рублей, "
                "себестоимость 600 рублей."
            ),
        }
    ]

    valid, error = validate_tool_arguments(
        tool_name="calculate_margin",
        arguments={
            "price": 1500,
            "cost": 1000,
        },
        messages=messages,
    )

    assert valid is False
    assert error is not None


def test_missing_cost_is_rejected():
    messages = [
        {
            "role": "user",
            "content": "Цена товара 1500 рублей.",
        }
    ]

    valid, error = validate_tool_arguments(
        tool_name="calculate_margin",
        arguments={
            "price": 1500,
        },
        messages=messages,
    )

    assert valid is False
    assert error is not None