from dataclasses import dataclass
import unicodedata
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
            "карточка",
            "карточку",
            "описание товара",
            "описание",
            "заголовок товара",
            "заголовок",
            "характеристик",
            "фото товара",
            "фото",
            "инфографик",
            "контент товара",
        ),
    ),
)


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text).lower().strip()


def route_request(text: str) -> str:
    normalized = normalize_text(text)

    for route in ROUTES:
        for keyword in route.keywords:
            if keyword in normalized:
                return route.name

    return "support"