# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP (Model Context Protocol) server that provides search capabilities for the Wake County Public Library catalog. The server exposes a single tool `search_library` that scrapes and parses the library's web catalog.

Built with Python using the official MCP Python SDK.

Inspired by: https://modelcontextprotocol.io/docs/develop/build-server

## Key Technologies
- Python 3.12+
- uv - Fast Python package manager: https://github.com/astral-sh/uv
- MCP Python SDK - Official Model Context Protocol SDK
- httpx - Async HTTP client
- BeautifulSoup4 - HTML parsing

## Key Commands

### Setup
```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --dev
```

### Add a Package
```bash
# Add runtime dependency
uv add <package-name>

# Add dev dependency
uv add --dev <package-name>
```

### Running the Server
```bash
# Run via uv
uv run python -m mcp_wcpl

# Or after activating virtual environment
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows
python -m mcp_wcpl
```

The server runs on stdio and is designed to be invoked by MCP clients (like Claude Desktop).

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/mcp_wcpl --cov-report=html

# Run specific test file
uv run pytest tests/test_server.py

# Run with verbose output
uv run pytest -v
```

## Architecture

### Project Structure
```
mcp-wcpl/
├── src/
│   └── mcp_wcpl/              # Main package
│       ├── __init__.py        # Package initialization
│       ├── server.py          # MCP server implementation
│       └── __main__.py        # Entry point
├── tests/                     # Test directory
│   ├── __init__.py
│   └── test_server.py
├── pyproject.toml             # Project configuration
├── .gitignore
├── README.md
└── CLAUDE.md
```

### Data Flow

```
MCP Client Request → Server (server.py) → Search Function → HTTP Fetch (httpx) →
Parse Results → BeautifulSoup HTML Parsing → Results → JSON Response
```

### Search Parameters

The `search_library` tool accepts:
- `query` (required): Search term
- `searchSource` (optional): `"local"` (default, Wake County only) or `"all"` (all NC Cardinal libraries)
- `limit` (optional): Max results to return (default: 10)

### HTML Parsing Strategy

The parser should use a fallback approach:
1. First attempts to parse with primary selectors (`.result`, `.result-title`, etc.)
2. Falls back to alternative selectors (`div[id^='result']`) if primary fails
3. Handles partial data gracefully (missing authors, formats, etc.)

This dual-selector strategy is critical for reliability since the library catalog HTML structure may vary.

## Important Implementation Details

1. **HTTP Headers**: The library website blocks requests without proper User-Agent headers. Include browser-like headers to avoid 403 errors.

2. **URL Construction**: The search URL format is:
   ```
   https://catalog.wake.gov/Union/Search?lookfor={query}&searchSource={local|all}
   ```

3. **MCP Tool Schema**: The tool definition includes a JSON schema that MCP clients use to understand parameters and generate UI.

4. **Async/Await**: The server uses async/await patterns throughout, as required by the MCP Python SDK.
