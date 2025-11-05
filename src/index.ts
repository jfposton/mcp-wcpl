#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { searchLibrary } from "./library-search.js";

/**
 * MCP Server for Wake County Public Library catalog search
 */
class WakeCountyLibraryServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: "wake-county-library",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
  }

  private setupHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "search_library",
          description: "Search the Wake County Public Library catalog for books, media, and other materials. Returns information about items including title, author, format, availability, and links to the catalog.",
          inputSchema: {
            type: "object",
            properties: {
              query: {
                type: "string",
                description: "The search term to look for (book title, author, keyword, etc.)",
              },
              searchSource: {
                type: "string",
                description: "Search source: 'local' for Wake County catalog only, or 'all' for all NC Cardinal libraries",
                enum: ["local", "all"],
                default: "local",
              },
              limit: {
                type: "number",
                description: "Maximum number of results to return (default: 10)",
                default: 10,
              },
            },
            required: ["query"],
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      if (request.params.name === "search_library") {
        const query = request.params.arguments?.query as string;
        const searchSource = (request.params.arguments?.searchSource as string) || "local";
        const limit = (request.params.arguments?.limit as number) || 10;

        if (!query) {
          throw new Error("Query parameter is required");
        }

        try {
          const results = await searchLibrary(query, searchSource, limit);

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(results, null, 2),
              },
            ],
          };
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : String(error);
          return {
            content: [
              {
                type: "text",
                text: `Error searching library: ${errorMessage}`,
              },
            ],
            isError: true,
          };
        }
      }

      throw new Error(`Unknown tool: ${request.params.name}`);
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Wake County Public Library MCP Server running on stdio");
  }
}

// Start the server
const server = new WakeCountyLibraryServer();
server.run().catch(console.error);
