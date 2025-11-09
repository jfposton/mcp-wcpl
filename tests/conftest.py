"""Shared test fixtures and utilities."""

from mcp_wcpl.scraper import ValidationError


class MockLibraryScraper:
    """Mock scraper for testing that returns fake data."""

    MOCK_DATA = [
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
    ]

    def search(
        self, query: str, search_source: str = "local", limit: int = 10
    ) -> list[dict[str, str]]:
        """Return mock search results.

        Args:
            query: Search term
            search_source: Search source
            limit: Maximum number of results to return

        Returns:
            List of mock book dictionaries

        Raises:
            ValidationError: If input parameters are invalid (matches real scraper behavior)
        """
        # Mimic real scraper validation
        if not query or not query.strip():
            raise ValidationError("Search query cannot be empty")

        if len(query) > 500:
            raise ValidationError("Search query too long (max 500 characters)")

        if search_source not in ("local", "all"):
            raise ValidationError("Invalid search source (must be 'local' or 'all')")

        if not isinstance(limit, int) or limit < 1:
            raise ValidationError("Limit must be a positive integer")

        if limit > 100:
            raise ValidationError("Limit too large (max 100)")

        return self.MOCK_DATA[:limit]
