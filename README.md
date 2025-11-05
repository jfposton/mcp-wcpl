# Wake County Public Library MCP Server

A Model Context Protocol (MCP) server that provides search capabilities for the Wake County Public Library catalog.

<a href="https://glama.ai/mcp/servers/@jfposton/mcp-wcpl-">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@jfposton/mcp-wcpl-/badge" alt="Wake County Public Library MCP server" />
</a>

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

## Installation

```bash
npm install
npm run build
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
      "command": "node",
      "args": ["/absolute/path/to/mcp-wake-county-library/dist/index.js"]
    }
  }
}
```

### With Other MCP Clients

Run the server using:

```bash
npm start
```

Or directly:

```bash
node dist/index.js
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

### Building

```bash
npm run build
```

### Project Structure

```
mcp-wake-county-library/
├── src/
│   └── index.ts          # Main server implementation
├── dist/                 # Compiled JavaScript output
├── package.json
├── tsconfig.json
└── README.md
```

## How It Works

The server:

1. Constructs search URLs for the Wake County library catalog
2. Fetches search results using appropriate HTTP headers
3. Parses the HTML response using Cheerio
4. Extracts relevant book information from the results
5. Returns structured JSON data

## License

MIT

## Links

- [Wake County Public Library](https://www.wakegov.com/departments-government/public-libraries)
- [Library Catalog](https://catalog.wake.gov/)
- [Model Context Protocol](https://modelcontextprotocol.io/)