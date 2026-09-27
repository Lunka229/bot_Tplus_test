
import asyncio

from app.mcp.client import MCPClient


async def main() -> None:
    client = MCPClient()

    try:
        tools = await client.list_tools()

        print("\nMCP TOOLS:")

        for tool in tools:
            print(f"\nName: {tool['name']}")
            print(f"Description: {tool['description']}")
            print(f"Schema: {tool['input_schema']}")

        result = await client.call_tool(
            "calculate_margin_tool",
            {
                "price": 1000,
                "cost": 600,
            },
        )

        print("\nMCP RESULT:")
        print(result)

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
