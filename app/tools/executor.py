import json
from typing import Any

from app.tools.calculator import calculate_margin


def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
) -> str:
    if tool_name == "calculate_margin":
        result = calculate_margin(
            price=float(arguments["price"]),
            cost=float(arguments["cost"]),
        )

        return json.dumps(
            {
                "price": result.price,
                "cost": result.cost,
                "profit": result.profit,
                "margin_percent": result.margin_percent,
                "markup_percent": result.markup_percent,
            },
            ensure_ascii=False,
        )

    raise ValueError(
        f"Unknown tool: {tool_name}"
    )