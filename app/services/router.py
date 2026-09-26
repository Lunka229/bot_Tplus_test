from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    name: str
    keywords: tuple[str, ...]


ROUTES = (
    Route(
        name="economics",
        keywords=(
            "маржинальность",
            "маржа",
            "себестоимость",
            "прибыль",
            "наценка",
            "экономика",
            "юнит",
            "unit",
        ),
    ),
    Route(
        name="marketing",
        keywords=(
            "реклама",
            "продвижение",
            "рк",
            "ctr",
            "конверсия",
            "реклам",
        ),
    ),
    Route(
        name="product_card",
        keywords=(
            "карточк",
            "описание товара",
            "заголовок товара",
            "характеристик",
            "фото товара",
            "инфографик",
            "контент товара",
        ),
    ),
)


def route_request(text: str) -> str:
    normalized = text.lower().strip()

    for route in ROUTES:
        for keyword in route.keywords:
            if keyword in normalized:
                return route.name

    return "support"