"""MCP server for LeetCode practice problem management."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Initialize MCP server
app = Server("interview-prep-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="hello",
            description="A simple hello world tool to verify MCP setup",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to greet",
                    }
                },
                "required": ["name"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "hello":
        user_name = arguments.get("name", "World")
        return [
            TextContent(
                type="text",
                text=f"Hello, {user_name}! The MCP server is working correctly.",
            )
        ]
    else:
        raise ValueError(f"Unknown tool: {name}")


async def async_main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Entry point for the MCP server."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()