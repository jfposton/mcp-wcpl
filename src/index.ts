#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fetch from "node-fetch";
import * as cheerio from "cheerio";

interface SearchResult {
  title: string;
  author?: string;
  format?: string;
  publicationYear?: string;
  availability?: string;
  url?: string;
  coverImage?: string;
}

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
          const results = await this.searchLibrary(query, searchSource, limit);

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

  private async searchLibrary(
    query: string,
    searchSource: string,
    limit: number
  ): Promise<SearchResult[]> {
    const searchUrl = `https://catalog.wake.gov/Union/Search?basicType=&genealogyType=&view=list&lookfor=${encodeURIComponent(query)}&searchSource=${searchSource}`;

    // Fetch the search results page with proper headers to avoid 403
    const response = await fetch(searchUrl, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const html = await response.text();
    const $ = cheerio.load(html);
    const results: SearchResult[] = [];

    // Parse search results from the HTML
    // The catalog uses a list view with result items
    $(".result").each((index, element) => {
      if (index >= limit) return false; // Stop after limit

      const $result = $(element);

      // Extract title
      const titleElement = $result.find(".result-title a");
      const title = titleElement.text().trim();
      const url = titleElement.attr("href");

      // Extract author
      const author = $result.find(".result-author").text().replace("by", "").trim();

      // Extract format
      const format = $result.find(".format").text().trim() ||
                    $result.find(".result-format").text().trim();

      // Extract publication year
      const pubYear = $result.find(".result-publication_year").text().trim() ||
                     $result.find(".publicationDate").text().trim();

      // Extract availability status
      const availability = $result.find(".status").text().trim() ||
                          $result.find(".availability-status").text().trim();

      // Extract cover image
      const coverImage = $result.find("img.book-cover, img.cover-image").attr("src");

      if (title) {
        results.push({
          title,
          author: author || undefined,
          format: format || undefined,
          publicationYear: pubYear || undefined,
          availability: availability || undefined,
          url: url ? `https://catalog.wake.gov${url}` : undefined,
          coverImage: coverImage || undefined,
        });
      }
    });

    // If no results found with the primary selector, try alternative patterns
    if (results.length === 0) {
      $("div[id^='result']").each((index, element) => {
        if (index >= limit) return false;

        const $result = $(element);

        const titleElement = $result.find("a.title, .result-title a, h2.title a, a[title]");
        const title = titleElement.first().text().trim() || titleElement.first().attr("title");
        const url = titleElement.first().attr("href");

        if (title) {
          results.push({
            title,
            author: $result.find(".author, .by").text().replace(/^by\s*/i, "").trim() || undefined,
            format: $result.find(".format, .mediaType").text().trim() || undefined,
            publicationYear: $result.find(".year, .date, .publicationDate").text().trim() || undefined,
            availability: $result.find(".status, .availability").text().trim() || undefined,
            url: url ? (url.startsWith("http") ? url : `https://catalog.wake.gov${url}`) : undefined,
            coverImage: $result.find("img").first().attr("src") || undefined,
          });
        }
      });
    }

    return results;
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
