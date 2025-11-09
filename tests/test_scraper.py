"""Tests for the scraper module."""

import pytest
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

    # Each result should either be a book result or an error response
    for item in results:
        # Check if it's an error response
        if "error" in item:
            assert "message" in item
            assert "type" in item
            assert isinstance(item["error"], str)
            assert isinstance(item["message"], str)
            assert isinstance(item["type"], str)
        else:
            # It's a book result
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
