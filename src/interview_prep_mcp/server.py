"""MCP server for LeetCode practice problem management."""

import asyncio
import json
from typing import Any, Dict, Union, List, cast
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .tools.load_problem import LoadProblemTool


# Initialize MCP server
app = Server("interview-prep-mcp")

# Initialize tools
load_problem_tool: LoadProblemTool = LoadProblemTool()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
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
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    if name == "load_problem":
        # Casts are still useful to give types to variables from the untyped 'arguments' dict
        title_slug = cast(Union[str, None], arguments.get("title_slug"))
        problem_id = cast(Union[int, None], arguments.get("problem_id"))
        problem_name = cast(Union[str, None], arguments.get("problem_name"))
        language = cast(Union[str, None], arguments.get("language"))

        if not title_slug and not problem_id and not problem_name:
            raise ValueError("Either title_slug, problem_id, or problem_name is required")

        try:
            result: Union[Dict[str, Any], List[Dict[str, Any]]] = await load_problem_tool.execute(
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


async def async_main() -> None:
    """Run the MCP server."""
    # Preload the problem cache on startup to hide latency
    await load_problem_tool.initialize()

    async with stdio_server() as streams:
        read_stream, write_stream = streams
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main() -> None:  # Added return type
    """Entry point for the MCP server."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()