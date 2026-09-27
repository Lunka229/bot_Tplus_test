from mcp.server.mcpserver import MCPServer

from app.tools.calculator import calculate_margin


mcp = MCPServer("Marketplace Tools")


@mcp.tool()
def calculate_margin_tool(
    price: float,
    cost: float,
) -> dict[str, float]:
    """Рассчитать прибыль, маржинальность и наценку товара."""

    result = calculate_margin(
        price=price,
        cost=cost,
    )

    return {
        "price": result.price,
        "cost": result.cost,
        "profit": result.profit,
        "margin_percent": result.margin_percent,
        "markup_percent": result.markup_percent,
    }


if __name__ == "__main__":
    mcp.run()