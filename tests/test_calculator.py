import pytest

from app.tools.calculator import calculate_margin


def test_calculate_margin():
    result = calculate_margin(
        price=1500,
        cost=600,
    )

    assert result.profit == 900
    assert result.margin_percent == 60
    assert result.markup_percent == 150


def test_zero_price():
    with pytest.raises(ValueError):
        calculate_margin(
            price=0,
            cost=600,
        )


def test_negative_cost():
    with pytest.raises(ValueError):
        calculate_margin(
            price=1500,
            cost=-100,
        )


def test_cost_greater_than_price():
    with pytest.raises(ValueError):
        calculate_margin(
            price=500,
            cost=600,
        )