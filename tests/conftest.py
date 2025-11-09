"""Shared test fixtures and utilities."""


class MockLibraryScraper:
    """Mock scraper for testing that returns fake data."""

    MOCK_DATA = [
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
    ]

    def search(self, query: str, search_source: str = "local", limit: int = 10) -> list[dict[str, str]]:
        """Return mock search results.

        Args:
            query: Search term (ignored in mock)
            search_source: Search source (ignored in mock)
            limit: Maximum number of results to return

        Returns:
            List of mock book dictionaries
        """
        return self.MOCK_DATA[:limit]
