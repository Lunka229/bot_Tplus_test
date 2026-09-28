import re
from typing import Any


def _normalize_number(value: float) -> float:
    return round(float(value), 2)


def _extract_value(
    text: str,
    patterns: list[str],
) -> float | None:
    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            value = match.group(1)
            value = value.replace(" ", "")
            value = value.replace(",", ".")

            try:
                return float(value)
            except ValueError:
                continue

    return None


def extract_known_values(
    messages: list[dict[str, Any]],
) -> dict[str, float]:
    """
    Извлекает явно указанные пользователем
    цену и себестоимость из контекста сообщений.
    """

    user_text = "\n".join(
        message.get("content", "")
        for message in messages
        if message.get("role") == "user"
    )

    price = _extract_value(
        user_text,
        [
            r"(?:цена\s+продажи)"
            r"\s*(?:товара)?\s*[:=]?\s*"
            r"(\d+(?:[.,]\d+)?)\s*(?:руб|рублей|₽)?",

            r"(?:цена)"
            r"\s*(?:товара)?\s*[:=]?\s*"
            r"(\d+(?:[.,]\d+)?)\s*(?:руб|рублей|₽)?",

            r"(?:стоимость\s+товара)"
            r"\s*[:=]?\s*"
            r"(\d+(?:[.,]\d+)?)\s*(?:руб|рублей|₽)?",

            r"(?:по\s+цене)"
            r"\s*[:=]?\s*"
            r"(\d+(?:[.,]\d+)?)\s*(?:руб|рублей|₽)?",
        ],
    )

    cost = _extract_value(
        user_text,
        [
            r"(?:себестоимость)"
            r"\s*[:=]?\s*"
            r"(\d+(?:[.,]\d+)?)\s*(?:руб|рублей|₽)?",

            r"(?:себестоимость\s+товара)"
            r"\s*[:=]?\s*"
            r"(\d+(?:[.,]\d+)?)\s*(?:руб|рублей|₽)?",
        ],
    )

    result: dict[str, float] = {}

    if price is not None:
        result["price"] = price

    if cost is not None:
        result["cost"] = cost

    return result


def validate_tool_arguments(
    tool_name: str,
    arguments: dict[str, Any],
    messages: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    """
    Проверяет, что аргументы tool были явно указаны
    пользователем или в сохранённом пользовательском контексте.
    """

    if tool_name != "calculate_margin":
        return True, None

    known_values = extract_known_values(messages)

    required_fields = ("price", "cost")

    for field in required_fields:
        if field not in arguments:
            return (
                False,
                f"Не указан обязательный параметр: {field}",
            )

        if field not in known_values:
            return (
                False,
                f"Параметр {field} не был явно указан "
                "пользователем.",
            )

        try:
            argument_value = _normalize_number(
                float(arguments[field])
            )
        except (TypeError, ValueError):
            return (
                False,
                f"Некорректное значение параметра: {field}",
            )

        known_value = _normalize_number(
            known_values[field]
        )

        if argument_value != known_value:
            return (
                False,
                f"Значение параметра {field} "
                f"({argument_value}) не совпадает "
                f"с указанным пользователем "
                f"значением ({known_value}).",
            )

    return True, None