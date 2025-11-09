"""Tests for the scraper module."""

from mcp_wcpl.scraper import WakeCountyLibraryScraper


def test_wake_county_scraper_initialization():
    """Test that WakeCountyLibraryScraper can be initialized."""
    scraper = WakeCountyLibraryScraper()
    assert scraper is not None
    assert scraper.timeout == 30.0

    custom_scraper = WakeCountyLibraryScraper(timeout=60.0)
    assert custom_scraper.timeout == 60.0


def test_wake_county_scraper_search_returns_list():
    """Test that WakeCountyLibraryScraper search returns a list."""
    scraper = WakeCountyLibraryScraper()
    results = scraper.search("python")

    assert isinstance(results, list)


def test_wake_county_scraper_result_structure():
    """Test that results have the expected structure."""
    scraper = WakeCountyLibraryScraper()
    results = scraper.search("test")

    # Should return at least something (even if it's an error)
    assert len(results) > 0

    # Each result should have the expected fields (both errors and books use same structure)
    for item in results:
        assert "title" in item
        assert "author" in item
        assert "format" in item
        assert "availability" in item
        assert isinstance(item["title"], str)
        assert isinstance(item["author"], str)
        assert isinstance(item["format"], str)
        assert isinstance(item["availability"], str)


def test_wake_county_scraper_respects_limit():
    """Test that limit parameter is respected."""
    scraper = WakeCountyLibraryScraper()
    results = scraper.search("fiction", limit=3)

    # Should return at most 3 results
    assert len(results) <= 3


def test_wake_county_scraper_search_sources():
    """Test that different search sources can be used."""
    scraper = WakeCountyLibraryScraper()

    # Both should work without errors
    local_results = scraper.search("test", search_source="local")
    all_results = scraper.search("test", search_source="all")

    assert isinstance(local_results, list)
    assert isinstance(all_results, list)


# Input validation tests
def test_wake_county_scraper_rejects_empty_query():
    """Test that empty queries are rejected."""
    scraper = WakeCountyLibraryScraper()

    result = scraper.search("")
    assert len(result) == 1
    assert "Error" in result[0]["title"]
    assert "empty" in result[0]["title"].lower()

    result_whitespace = scraper.search("   ")
    assert len(result_whitespace) == 1
    assert "Error" in result_whitespace[0]["title"]


def test_wake_county_scraper_rejects_long_query():
    """Test that excessively long queries are rejected."""
    scraper = WakeCountyLibraryScraper()

    long_query = "a" * 501
    result = scraper.search(long_query)

    assert len(result) == 1
    assert "Error" in result[0]["title"]
    assert "too long" in result[0]["title"].lower()


def test_wake_county_scraper_rejects_invalid_search_source():
    """Test that invalid search sources are rejected."""
    scraper = WakeCountyLibraryScraper()

    result = scraper.search("test", search_source="invalid")
    assert len(result) == 1
    assert "Error" in result[0]["title"]
    assert "search source" in result[0]["title"].lower()


def test_wake_county_scraper_rejects_negative_limit():
    """Test that negative limits are rejected."""
    scraper = WakeCountyLibraryScraper()

    result = scraper.search("test", limit=-1)
    assert len(result) == 1
    assert "Error" in result[0]["title"]
    assert "positive integer" in result[0]["title"].lower()


def test_wake_county_scraper_rejects_zero_limit():
    """Test that zero limit is rejected."""
    scraper = WakeCountyLibraryScraper()

    result = scraper.search("test", limit=0)
    assert len(result) == 1
    assert "Error" in result[0]["title"]


def test_wake_county_scraper_rejects_excessive_limit():
    """Test that excessively large limits are rejected."""
    scraper = WakeCountyLibraryScraper()

    result = scraper.search("test", limit=101)
    assert len(result) == 1
    assert "Error" in result[0]["title"]
    assert "too large" in result[0]["title"].lower()


def test_wake_county_scraper_accepts_max_valid_limit():
    """Test that the maximum valid limit (100) is accepted."""
    scraper = WakeCountyLibraryScraper()

    result = scraper.search("test", limit=100)
    # Should not be an error message
    if len(result) == 1 and "Error" in result[0].get("title", ""):
        # If it's an error, it should be about connection, not validation
        assert "too large" not in result[0]["title"].lower()


def test_wake_county_scraper_error_messages_are_sanitized():
    """Test that error messages don't expose internal details."""
    scraper = WakeCountyLibraryScraper()

    # Test with various invalid inputs
    test_cases = [
        ("", "empty query"),
        ("a" * 501, "long query"),
    ]

    for query, description in test_cases:
        result = scraper.search(query)
        error_msg = result[0]["title"].lower()

        # Should not contain paths, exceptions, or stack traces
        assert "/" not in error_msg, f"Error for {description} contains path"
        assert "\\" not in error_msg, f"Error for {description} contains path"
        assert "traceback" not in error_msg, f"Error for {description} contains traceback"
        assert "exception" not in error_msg, f"Error for {description} exposes exception type"
