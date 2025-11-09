"""Tests for the scraper module."""

import pytest

from mcp_wcpl.scraper import NetworkError, ScraperError, ValidationError, WakeCountyLibraryScraper


def test_wake_county_scraper_initialization():
    """Test that WakeCountyLibraryScraper can be initialized."""
    scraper = WakeCountyLibraryScraper()
    assert scraper is not None
    assert scraper.timeout == 30.0

    custom_scraper = WakeCountyLibraryScraper(timeout=60.0)
    assert custom_scraper.timeout == 60.0


def test_wake_county_scraper_search_returns_list():
    """Test that WakeCountyLibraryScraper search returns a list or raises an exception."""
    scraper = WakeCountyLibraryScraper()

    try:
        results = scraper.search("python")
        assert isinstance(results, list)
        # If we get results, verify they're books
        if len(results) > 0:
            assert "title" in results[0]
    except (NetworkError, ScraperError):
        # Network errors are expected since we're making real requests
        pass


def test_wake_county_scraper_result_structure():
    """Test that results have the expected structure (when accessible)."""
    scraper = WakeCountyLibraryScraper()

    try:
        results = scraper.search("test")

        # Should return a list
        assert isinstance(results, list)
        assert len(results) > 0

        # Each result should be a book with all required fields
        for item in results:
            assert "title" in item
            assert "author" in item
            assert "format" in item
            assert "availability" in item
            assert isinstance(item["title"], str)
            assert isinstance(item["author"], str)
            assert isinstance(item["format"], str)
            assert isinstance(item["availability"], str)
    except (NetworkError, ScraperError):
        # Network errors are expected since we're making real requests
        pass


def test_wake_county_scraper_respects_limit():
    """Test that limit parameter is respected (when accessible)."""
    scraper = WakeCountyLibraryScraper()

    try:
        results = scraper.search("fiction", limit=3)
        # Should return at most 3 results
        assert len(results) <= 3
    except (NetworkError, ScraperError):
        # Network errors are expected
        pass


def test_wake_county_scraper_search_sources():
    """Test that different search sources can be used (when accessible)."""
    scraper = WakeCountyLibraryScraper()

    # Both should either work or raise network errors (not validation errors)
    for source in ["local", "all"]:
        try:
            results = scraper.search("test", search_source=source)
            assert isinstance(results, list)
        except (NetworkError, ScraperError):
            # Network errors are expected
            pass


# Input validation tests
def test_wake_county_scraper_rejects_empty_query():
    """Test that empty queries raise ValidationError."""
    scraper = WakeCountyLibraryScraper()

    with pytest.raises(ValidationError, match="empty"):
        scraper.search("")

    with pytest.raises(ValidationError):
        scraper.search("   ")


def test_wake_county_scraper_rejects_long_query():
    """Test that excessively long queries raise ValidationError."""
    scraper = WakeCountyLibraryScraper()

    long_query = "a" * 501
    with pytest.raises(ValidationError, match="too long"):
        scraper.search(long_query)


def test_wake_county_scraper_rejects_invalid_search_source():
    """Test that invalid search sources raise ValidationError."""
    scraper = WakeCountyLibraryScraper()

    with pytest.raises(ValidationError, match="search source"):
        scraper.search("test", search_source="invalid")


def test_wake_county_scraper_rejects_negative_limit():
    """Test that negative limits raise ValidationError."""
    scraper = WakeCountyLibraryScraper()

    with pytest.raises(ValidationError, match="positive integer"):
        scraper.search("test", limit=-1)


def test_wake_county_scraper_rejects_zero_limit():
    """Test that zero limit raises ValidationError."""
    scraper = WakeCountyLibraryScraper()

    with pytest.raises(ValidationError):
        scraper.search("test", limit=0)


def test_wake_county_scraper_rejects_excessive_limit():
    """Test that excessively large limits raise ValidationError."""
    scraper = WakeCountyLibraryScraper()

    with pytest.raises(ValidationError, match="too large"):
        scraper.search("test", limit=101)


def test_wake_county_scraper_accepts_max_valid_limit():
    """Test that the maximum valid limit (100) is accepted."""
    scraper = WakeCountyLibraryScraper()

    # Should not raise a validation error (may raise network error though)
    try:
        result = scraper.search("test", limit=100)
        assert isinstance(result, list)
    except (NetworkError, ScraperError):
        # Network/scraper errors are fine - we're testing validation
        pass


def test_validation_error_messages_are_sanitized():
    """Test that validation error messages don't expose internal details."""
    scraper = WakeCountyLibraryScraper()

    # Test with various invalid inputs
    test_cases = [
        ("", "empty query"),
        ("a" * 501, "long query"),
    ]

    for query, description in test_cases:
        try:
            scraper.search(query)
            pytest.fail(f"Expected ValidationError for {description}")
        except ValidationError as e:
            error_msg = str(e).lower()

            # Should not contain paths, exceptions, or stack traces
            assert "/" not in error_msg, f"Error for {description} contains path"
            assert "\\" not in error_msg, f"Error for {description} contains path"
            assert "traceback" not in error_msg, f"Error for {description} contains traceback"
