"""Library catalog scraping functionality.

This module provides the interface and implementation for searching the Wake County
Public Library catalog.
"""

import logging

import httpx
from bs4 import BeautifulSoup

# Configure logging for internal error details
logger = logging.getLogger(__name__)


class WakeCountyLibraryScraper:
    """Scraper for Wake County Public Library catalog."""

    BASE_URL = "https://catalog.wake.gov/Union/Search"

    # Browser-like headers to avoid 403 errors
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self, timeout: float = 30.0):
        """Initialize the scraper.

        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout

    def search(
        self, query: str, search_source: str = "local", limit: int = 10
    ) -> list[dict[str, str]]:
        """Search the library catalog.

        Args:
            query: Search term
            search_source: 'local' for Wake County only, 'all' for all NC Cardinal libraries
            limit: Maximum number of results to return

        Returns:
            List of dictionaries with keys: title, author, format, availability
        """
        # Input validation
        if not query or not query.strip():
            return [{"error": "Search query cannot be empty"}]

        # Validate query length (most URLs have ~2000 char limit, be conservative)
        if len(query) > 500:
            return [{"error": "Search query too long (max 500 characters)"}]

        # Validate search source
        if search_source not in ("local", "all"):
            return [{"error": "Invalid search source (must be 'local' or 'all')"}]

        # Validate limit
        if not isinstance(limit, int) or limit < 1:
            return [{"error": "Limit must be a positive integer"}]

        if limit > 100:
            return [{"error": "Limit too large (max 100)"}]

        params = {"lookfor": query.strip(), "searchSource": search_source, "view": "list"}

        try:
            response = httpx.get(
                self.BASE_URL,
                params=params,
                headers=self.HEADERS,
                timeout=self.timeout,
                follow_redirects=True,
            )
            response.raise_for_status()
            results = self._parse_results(response.text)
            return results[:limit]

        except httpx.HTTPError as e:
            # Log detailed error internally for debugging
            logger.error(f"HTTP error during library search: {e}", exc_info=True)
            # Return sanitized error to user
            return [{"error": "Unable to connect to library catalog"}]
        except Exception as e:
            # Log detailed error internally for debugging
            logger.error(f"Unexpected error during library search: {e}", exc_info=True)
            # Return generic sanitized error to user
            return [{"error": "Search failed. Please try again later"}]

    def _parse_results(self, html: str) -> list[dict[str, str]]:
        """Parse HTML search results.

        Args:
            html: HTML content from the library catalog

        Returns:
            List of dictionaries containing book information
        """
        soup = BeautifulSoup(html, "lxml")
        results = []

        # Try primary selector first, then fallback to alternative
        result_items = soup.select(".result")
        if not result_items:
            result_items = soup.select('div[id^="result"]')

        for item in result_items:
            # Extract title
            title_elem = item.select_one(".result-title a, .title a")
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"

            # Extract author
            author_elem = item.select_one(".result-author, .author")
            author = author_elem.get_text(strip=True) if author_elem else "Unknown Author"
            # Clean up "by " prefix if present
            if author.lower().startswith("by "):
                author = author[3:].strip()

            # Extract format
            format_elem = item.select_one(".result-format, .format, .iconlabel")
            format_type = format_elem.get_text(strip=True) if format_elem else "Unknown Format"

            # Extract availability
            availability_elem = item.select_one(".status, .availability")
            availability = (
                availability_elem.get_text(strip=True) if availability_elem else "Unknown"
            )

            results.append(
                {
                    "title": title,
                    "author": author,
                    "format": format_type,
                    "availability": availability,
                }
            )

        return results
