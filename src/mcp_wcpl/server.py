"""MCP server implementation for Wake County Public Library search.

This module provides the MCP server that exposes library search functionality.
"""

from mcp.server.fastmcp import FastMCP

from mcp_wcpl.scraper import WakeCountyLibraryScraper

# Initialize the MCP server
mcp = FastMCP("mcp-wcpl")

# Initialize the scraper
scraper = WakeCountyLibraryScraper()


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
    return scraper.search(query, searchSource, limit)
