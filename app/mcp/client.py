from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """Клиент для подключения к локальному MCP Server через stdio."""

    def __init__(self) -> None:
        self._session: ClientSession | None = None
        self._stdio_context = None
        self._session_context = None

    async def connect(self) -> None:
        if self._session is not None:
            return

        project_root = Path(__file__).resolve().parents[2]

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[
                "-m",
                "app.mcp.server",
            ],
            cwd=str(project_root),
        )

        self._stdio_context = stdio_client(server_params)

        read_stream, write_stream = (
            await self._stdio_context.__aenter__()
        )

        self._session_context = ClientSession(
            read_stream,
            write_stream,
        )

        self._session = (
            await self._session_context.__aenter__()
        )

        await self._session.initialize()

    async def list_tools(self) -> list[dict[str, Any]]:
        await self.connect()

        assert self._session is not None

        result = await self._session.list_tools()

        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in result.tools
        ]

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        await self.connect()

        assert self._session is not None

        return await self._session.call_tool(
            tool_name,
            arguments=arguments,
        )

    async def close(self) -> None:
        if self._session_context is not None:
            await self._session_context.__aexit__(
                None,
                None,
                None,
            )
            self._session_context = None
            self._session = None

        if self._stdio_context is not None:
            await self._stdio_context.__aexit__(
                None,
                None,
                None,
            )
            self._stdio_context = None

