import asyncio

from app.mcp.client import MCPClient


async def main() -> None:
    client = MCPClient()

    try:
        print("=== LIST TOOLS ===")

        tools = await client.list_tools()

        for tool in tools:
            print(tool)

        print()
        print("=== CALL TOOL ===")

        result = await client.call_tool(
            "calculate_margin_tool",
            {
                "price": 1000,
                "cost": 600,
            },
        )

        print("TYPE:", type(result))
        print("RESULT:", repr(result))
        print("IS NONE:", result is None)
        print("IS ERROR:", getattr(result, "is_error", "NO ATTRIBUTE"))
        print(
            "STRUCTURED:",
            repr(getattr(result, "structured_content", "NO ATTRIBUTE")),
        )
        print(
            "CONTENT:",
            repr(getattr(result, "content", "NO ATTRIBUTE")),
        )

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())