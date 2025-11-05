import fetch from "node-fetch";
import * as cheerio from "cheerio";

export interface SearchResult {
  title: string;
  author?: string;
  format?: string;
  publicationYear?: string;
  availability?: string;
  url?: string;
  coverImage?: string;
}

/**
 * Parse HTML content from library search results
 */
export function parseSearchResults(html: string, limit: number): SearchResult[] {
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

/**
 * Search the Wake County Public Library catalog
 */
export async function searchLibrary(
  query: string,
  searchSource: string = "local",
  limit: number = 10
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
  return parseSearchResults(html, limit);
}
