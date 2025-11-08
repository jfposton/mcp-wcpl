"""MCP server implementation for Wake County Public Library search.

This module provides the MCP server that exposes library search functionality.
"""

import asyncio
from typing import Any, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio


# Mock data for testing
MOCK_LIBRARY_DATA = [
    {
        "title": "Python Programming: An Introduction to Computer Science",
        "author": "John Zelle",
        "format": "Book",
        "availability": "Available"
    },
    {
        "title": "Learning Python",
        "author": "Mark Lutz",
        "format": "Book",
        "availability": "Checked Out"
    },
    {
        "title": "Python Crash Course",
        "author": "Eric Matthes",
        "format": "eBook",
        "availability": "Available"
    },
    {
        "title": "Automate the Boring Stuff with Python",
        "author": "Al Sweigart",
        "format": "Book",
        "availability": "Available"
    },
    {
        "title": "Fluent Python",
        "author": "Luciano Ramalho",
        "format": "Book",
        "availability": "Available"
    },
    {
        "title": "Effective Python",
        "author": "Brett Slatkin",
        "format": "Book",
        "availability": "Checked Out"
    },
    {
        "title": "Python Cookbook",
        "author": "David Beazley",
        "format": "Book",
        "availability": "Available"
    },
    {
        "title": "Python for Data Analysis",
        "author": "Wes McKinney",
        "format": "eBook",
        "availability": "Available"
    },
    {
        "title": "Introduction to Machine Learning with Python",
        "author": "Andreas Müller",
        "format": "Book",
        "availability": "Available"
    },
    {
        "title": "Django for Beginners",
        "author": "William Vincent",
        "format": "Book",
        "availability": "Available"
    },
]


async def search_library(
    query: str,
    searchSource: str = "local",
    limit: int = 10
) -> list[dict[str, str]]:
    """Search the library catalog and return results.

    Args:
        query: Search term
        searchSource: "local" for Wake County only, "all" for all NC Cardinal libraries
        limit: Maximum number of results to return (default: 10)

    Returns:
        List of dictionaries containing book information with keys:
        - title: Book title
        - author: Book author
        - format: Format (Book, eBook, etc.)
        - availability: Availability status
    """
    # Return mock data, limited by the limit parameter
    return MOCK_LIBRARY_DATA[:limit]


def create_server() -> Server:
    """Create and configure the MCP server.

    Returns:
        Configured MCP Server instance
    """
    server = Server("mcp-wcpl")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools.

        Returns:
            List of available tools
        """
        return [
            Tool(
                name="search_library",
                description="Search the Wake County Public Library catalog for books and other materials",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search term to look for in the library catalog"
                        },
                        "searchSource": {
                            "type": "string",
                            "description": "Search scope: 'local' for Wake County only, 'all' for all NC Cardinal libraries",
                            "enum": ["local", "all"],
                            "default": "local"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50
                        }
                    },
                    "required": ["query"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls.

        Args:
            name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            List of TextContent with the results

        Raises:
            ValueError: If tool name is unknown
        """
        if name != "search_library":
            raise ValueError(f"Unknown tool: {name}")

        query = arguments.get("query")
        if not query:
            raise ValueError("query parameter is required")

        search_source = arguments.get("searchSource", "local")
        limit = arguments.get("limit", 10)

        results = await search_library(query, search_source, limit)

        # Format results as JSON string
        import json
        results_json = json.dumps(results, indent=2)

        return [
            TextContent(
                type="text",
                text=results_json
            )
        ]

    return server


async def main():
    """Main entry point for the MCP server.

    Runs the server using stdio transport.
    """
    server = create_server()

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
