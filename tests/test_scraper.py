"""Tests for the scraper module."""

import pytest
from mcp_wcpl.scraper import MockLibraryScraper, WakeCountyLibraryScraper


def test_mock_scraper_returns_results():
    """Test that MockLibraryScraper returns expected structure."""
    scraper = MockLibraryScraper()
    results = scraper.search("test query")

    assert isinstance(results, list)
    assert len(results) > 0


def test_mock_scraper_respects_limit():
    """Test that MockLibraryScraper respects the limit parameter."""
    scraper = MockLibraryScraper()

    results_2 = scraper.search("test", limit=2)
    assert len(results_2) == 2

    results_1 = scraper.search("test", limit=1)
    assert len(results_1) == 1


def test_mock_scraper_result_structure():
    """Test that MockLibraryScraper returns correct data structure."""
    scraper = MockLibraryScraper()
    results = scraper.search("test")

    for item in results:
        assert "title" in item
        assert "author" in item
        assert "format" in item
        assert "availability" in item
        assert isinstance(item["title"], str)
        assert isinstance(item["author"], str)
        assert isinstance(item["format"], str)
        assert isinstance(item["availability"], str)
        assert len(item["title"]) > 0
        assert len(item["author"]) > 0
        assert len(item["format"]) > 0
        assert len(item["availability"]) > 0


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

    # Each result should have the required fields
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
