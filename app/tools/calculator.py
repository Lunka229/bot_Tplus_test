from dataclasses import dataclass


@dataclass(frozen=True)
class MarginResult:
    price: float
    cost: float
    profit: float
    margin_percent: float
    markup_percent: float


def calculate_margin(
    price: float,
    cost: float,
) -> MarginResult:
    if price <= 0:
        raise ValueError("Цена должна быть больше нуля.")

    if cost < 0:
        raise ValueError(
            "Себестоимость не может быть отрицательной."
        )

    if cost > price:
        raise ValueError(
            "Себестоимость не может быть больше цены "
            "в рамках этого простого расчёта."
        )

    profit = price - cost

    margin_percent = (
        profit / price * 100
    )

    markup_percent = (
        profit / cost * 100
        if cost > 0
        else 0.0
    )

    return MarginResult(
        price=price,
        cost=cost,
        profit=profit,
        margin_percent=margin_percent,
        markup_percent=markup_percent,
    )