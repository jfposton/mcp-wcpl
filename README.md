# Wake County Public Library MCP Server

A Model Context Protocol (MCP) server that provides search capabilities for the Wake County Public Library catalog.

Built with Python using the official MCP Python SDK and uv for dependency management.

## Features

- Search the Wake County Public Library catalog
- Search local Wake County catalog or all NC Cardinal libraries
- Returns detailed information including:
  - Title
  - Author
  - Format (book, DVD, audiobook, etc.)
  - Publication year
  - Availability status
  - Direct links to catalog entries
  - Cover images

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

### Installing uv

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcp-wcpl

# Install dependencies
uv sync
```

## Usage

### With Claude Desktop

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "wake-county-library": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-wcpl",
        "run",
        "python",
        "-m",
        "mcp_wcpl"
      ]
    }
  }
}
```

Replace `/absolute/path/to/mcp-wcpl` with the actual path to this project directory.

### Running Directly

You can also run the server directly for testing:

```bash
# Using uv (recommended)
uv run python -m mcp_wcpl

# Or activate the virtual environment first
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate     # Windows
python -m mcp_wcpl
```

## Available Tools

### `search_library`

Search the Wake County Public Library catalog.

**Parameters:**

- `query` (string, required): The search term (book title, author, keyword, etc.)
- `searchSource` (string, optional):
  - `"local"` (default) - Search only Wake County catalog
  - `"all"` - Search all NC Cardinal libraries
- `limit` (number, optional): Maximum number of results to return (default: 10)

**Example:**

```json
{
  "query": "Foundation Isaac Asimov",
  "searchSource": "local",
  "limit": 5
}
```

**Response:**

Returns an array of search results with the following structure:

```json
[
  {
    "title": "Foundation",
    "author": "Asimov, Isaac",
    "format": "Book",
    "publicationYear": "2004",
    "availability": "Available",
    "url": "https://catalog.wake.gov/Union/Record/...",
    "coverImage": "https://..."
  }
]
```

## Development

### Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage report
uv run pytest --cov=src/mcp_wcpl --cov-report=html

# Run specific test file
uv run pytest tests/test_server.py
```

The test suite will include:
- Unit tests for HTML parsing logic
- Integration tests for search functionality with mocked HTTP requests
- Tests for MCP server tool interface
- Error handling tests

### Adding Dependencies

```bash
# Add a runtime dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>
```

### Project Structure

```
mcp-wcpl/
├── src/
│   └── mcp_wcpl/             # Main package
│       ├── __init__.py       # Package initialization
│       ├── __main__.py       # Entry point
│       └── server.py         # MCP server implementation
├── tests/                    # Test files
│   ├── __init__.py
│   └── test_server.py
├── .venv/                    # Virtual environment (created by uv)
├── pyproject.toml            # Project configuration
├── uv.lock                   # Dependency lock file
├── .gitignore
├── README.md
└── CLAUDE.md                 # Instructions for Claude Code
```

## How It Works

The server will:

1. Construct search URLs for the Wake County library catalog
2. Fetch search results using httpx with appropriate HTTP headers
3. Parse the HTML response using BeautifulSoup4
4. Extract relevant book information from the results
5. Return structured JSON data via the MCP protocol

## License

MIT

## Links

- [Wake County Public Library](https://www.wakegov.com/departments-government/public-libraries)
- [Library Catalog](https://catalog.wake.gov/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
