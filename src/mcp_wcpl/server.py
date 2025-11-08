"""MCP server implementation for Wake County Public Library search.

This module provides the MCP server that exposes library search functionality.
"""

from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("mcp-wcpl")

# Mock data for testing
MOCK_LIBRARY_DATA = [
    {
        "title": "Python Programming: An Introduction to Computer Science",
        "author": "John Zelle",
        "format": "Book",
        "availability": "Available",
    },
    {
        "title": "Learning Python",
        "author": "Mark Lutz",
        "format": "Book",
        "availability": "Checked Out",
    },
    {
        "title": "Python Crash Course",
        "author": "Eric Matthes",
        "format": "eBook",
        "availability": "Available",
    },
    {
        "title": "Automate the Boring Stuff with Python",
        "author": "Al Sweigart",
        "format": "Book",
        "availability": "Available",
    },
    {
        "title": "Fluent Python",
        "author": "Luciano Ramalho",
        "format": "Book",
        "availability": "Available",
    },
    {
        "title": "Effective Python",
        "author": "Brett Slatkin",
        "format": "Book",
        "availability": "Checked Out",
    },
    {
        "title": "Python Cookbook",
        "author": "David Beazley",
        "format": "Book",
        "availability": "Available",
    },
    {
        "title": "Python for Data Analysis",
        "author": "Wes McKinney",
        "format": "eBook",
        "availability": "Available",
    },
    {
        "title": "Introduction to Machine Learning with Python",
        "author": "Andreas Müller",
        "format": "Book",
        "availability": "Available",
    },
    {
        "title": "Django for Beginners",
        "author": "William Vincent",
        "format": "Book",
        "availability": "Available",
    },
]


@mcp.tool()
def search_library(
    query: str, searchSource: str = "local", limit: int = 10
) -> list[dict[str, str]]:
    """Search the Wake County Public Library catalog for books and other materials.

    Args:
        query: The search term to look for in the library catalog
        searchSource: Search scope - 'local' for Wake County only, 'all' for all NC
            Cardinal libraries (default: 'local')
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
