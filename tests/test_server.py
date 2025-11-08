"""Tests for the MCP server."""

import pytest
from mcp_wcpl.server import create_server, search_library


@pytest.mark.asyncio
async def test_server_creation():
    """Test that the MCP server can be created successfully."""
    server = create_server()

    # Verify server was created
    assert server is not None
    assert server.name == "mcp-wcpl"


@pytest.mark.asyncio
async def test_search_library_with_basic_query():
    """Test search_library with a basic query."""
    result = await search_library("python programming")

    # Verify result structure
    assert isinstance(result, list)
    assert len(result) > 0

    # Verify each result has expected fields
    for item in result:
        assert "title" in item
        assert "author" in item
        assert "format" in item
        assert "availability" in item
        assert isinstance(item["title"], str)
        assert isinstance(item["author"], str)
        assert isinstance(item["format"], str)
        assert isinstance(item["availability"], str)


@pytest.mark.asyncio
async def test_search_library_with_limit():
    """Test search_library respects the limit parameter."""
    limit = 3
    result = await search_library("fiction", limit=limit)

    assert isinstance(result, list)
    assert len(result) <= limit


@pytest.mark.asyncio
async def test_search_library_with_search_source_local():
    """Test search_library with local search source."""
    result = await search_library("mystery", searchSource="local")

    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_search_library_with_search_source_all():
    """Test search_library with all NC Cardinal libraries search source."""
    result = await search_library("science fiction", searchSource="all")

    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_search_library_default_limit():
    """Test search_library uses default limit of 10."""
    result = await search_library("books")

    assert isinstance(result, list)
    assert len(result) <= 10


@pytest.mark.asyncio
async def test_search_library_result_fields():
    """Test that search results contain all expected fields with correct types."""
    result = await search_library("test query")

    assert len(result) > 0

    first_result = result[0]

    # Check all required fields exist
    required_fields = ["title", "author", "format", "availability"]
    for field in required_fields:
        assert field in first_result
        assert isinstance(first_result[field], str)
        assert len(first_result[field]) > 0


@pytest.mark.asyncio
async def test_search_library_returns_valid_json_structure():
    """Test that the search results are JSON-serializable."""
    import json

    result = await search_library("test")

    # Should be able to serialize to JSON without errors
    json_str = json.dumps(result)

    # Should be able to deserialize back
    parsed = json.loads(json_str)

    assert parsed == result
