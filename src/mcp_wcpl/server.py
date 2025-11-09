"""MCP server implementation for Wake County Public Library search.

This module provides the MCP server that exposes library search functionality.
"""

import logging

from mcp.server.fastmcp import FastMCP

from mcp_wcpl.scraper import ScraperError, ValidationError, WakeCountyLibraryScraper

# Configure logging
logger = logging.getLogger(__name__)

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

        Or a single-item list with an error dictionary:
        - error: Error message
    """
    try:
        return scraper.search(query, searchSource, limit)
    except ValidationError as e:
        # Log validation errors at info level (user errors, not system errors)
        logger.info(f"Validation error: {e}")
        return [{"error": str(e)}]
    except ScraperError as e:
        # Log scraper errors at error level
        logger.error(f"Scraper error: {e}", exc_info=True)
        return [{"error": str(e)}]
    except Exception as e:
        # Catch any unexpected errors to ensure we never crash
        logger.error(f"Unexpected error in search_library: {e}", exc_info=True)
        return [{"error": "An unexpected error occurred. Please try again later"}]
