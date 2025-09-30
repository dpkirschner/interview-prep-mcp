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
            description="Load a LeetCode problem by its title slug, problem ID, or search by name. Optionally specify a language to get code for that language only.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title_slug": {
                        "type": "string",
                        "description": "The URL-friendly slug of the problem (e.g., 'two-sum')",
                    },
                    "problem_id": {
                        "type": "integer",
                        "description": "The problem ID number (e.g., 1 for Two Sum)",
                    },
                    "problem_name": {
                        "type": "string",
                        "description": "Search for problems by name or title (e.g., 'two sum'). Returns multiple matches if found.",
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language for code snippet (e.g., 'python', 'java', 'golang', 'cpp'). If omitted, returns all available code snippets.",
                    }
                },
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
        problem_id = arguments.get("problem_id")
        problem_name = arguments.get("problem_name")
        language = arguments.get("language")

        if not title_slug and not problem_id and not problem_name:
            raise ValueError("Either title_slug, problem_id, or problem_name is required")

        try:
            result = await load_problem_tool.execute(
                title_slug=title_slug,
                problem_id=problem_id,
                problem_name=problem_name,
                language=language
            )
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
    # Preload the problem cache on startup to hide latency
    await load_problem_tool.initialize()

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