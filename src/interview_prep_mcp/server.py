"""MCP server for LeetCode practice problem management."""

import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .tools.load_problem import LoadProblemTool


# Initialize MCP server
app = Server("interview-prep-mcp")

# Initialize tools
load_problem_tool = LoadProblemTool()


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
        ),
        Tool(
            name="load_problem",
            description="Load a LeetCode problem by its title slug (e.g., 'two-sum', 'reverse-linked-list')",
            inputSchema={
                "type": "object",
                "properties": {
                    "title_slug": {
                        "type": "string",
                        "description": "The URL-friendly slug of the problem (e.g., 'two-sum')",
                    }
                },
                "required": ["title_slug"],
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
    elif name == "load_problem":
        title_slug = arguments.get("title_slug")
        if not title_slug:
            raise ValueError("title_slug is required")

        try:
            result = await load_problem_tool.execute(title_slug)
            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2),
                )
            ]
        except Exception as e:
            raise ValueError(f"Failed to load problem: {str(e)}")
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