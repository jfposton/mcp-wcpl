import { describe, it, expect, jest, beforeEach } from '@jest/globals';
import { parseSearchResults, searchLibrary, SearchResult } from '../library-search.js';
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

describe('parseSearchResults', () => {
  let mockHtml: string;

  beforeEach(() => {
    // Load mock HTML
    mockHtml = readFileSync(
      join(__dirname, 'mocks', 'searchResults.html'),
      'utf-8'
    );
  });

  it('should parse search results correctly', () => {
    const results = parseSearchResults(mockHtml, 10);

    expect(results).toHaveLength(3);

    // Check first result
    expect(results[0]).toEqual({
      title: 'Foundation',
      author: 'Asimov, Isaac',
      format: 'Book',
      publicationYear: '2004',
      availability: 'Available',
      url: 'https://catalog.wake.gov/Union/Record/123',
      coverImage: 'https://example.com/cover1.jpg',
    });

    // Check second result
    expect(results[1]).toEqual({
      title: 'The Hobbit',
      author: 'Tolkien, J.R.R.',
      format: 'Book',
      publicationYear: '1937',
      availability: 'Checked Out',
      url: 'https://catalog.wake.gov/Union/Record/456',
      coverImage: 'https://example.com/cover2.jpg',
    });

    // Check third result
    expect(results[2]).toEqual({
      title: 'Dune',
      author: 'Herbert, Frank',
      format: 'Audiobook',
      publicationYear: '1965',
      availability: 'Available',
      url: 'https://catalog.wake.gov/Union/Record/789',
      coverImage: 'https://example.com/cover3.jpg',
    });
  });

  it('should respect the limit parameter', () => {
    const results = parseSearchResults(mockHtml, 2);
    expect(results).toHaveLength(2);
    expect(results[0].title).toBe('Foundation');
    expect(results[1].title).toBe('The Hobbit');
  });

  it('should handle empty HTML', () => {
    const results = parseSearchResults('<html><body></body></html>', 10);
    expect(results).toHaveLength(0);
  });

  it('should handle HTML with no matching selectors', () => {
    const results = parseSearchResults(
      '<html><body><div>No results found</div></body></html>',
      10
    );
    expect(results).toHaveLength(0);
  });

  it('should handle partial data in results', () => {
    const partialHtml = `
      <html>
        <body>
          <div class="result">
            <div class="result-title">
              <a href="/Union/Record/999">Test Book</a>
            </div>
          </div>
        </body>
      </html>
    `;

    const results = parseSearchResults(partialHtml, 10);
    expect(results).toHaveLength(1);
    expect(results[0]).toEqual({
      title: 'Test Book',
      url: 'https://catalog.wake.gov/Union/Record/999',
    });
  });

  it('should strip "by" from author field', () => {
    const results = parseSearchResults(mockHtml, 10);
    // Verify that "by" is removed from the author names
    results.forEach(result => {
      if (result.author) {
        expect(result.author).not.toMatch(/^by\s+/i);
      }
    });
  });
});

describe('searchLibrary', () => {
  // Mock node-fetch
  const mockFetch = jest.fn() as jest.MockedFunction<typeof fetch>;

  beforeEach(() => {
    jest.clearAllMocks();
    // Replace global fetch with our mock
    global.fetch = mockFetch as any;
  });

  it('should fetch and parse search results', async () => {
    const mockHtml = readFileSync(
      join(__dirname, 'mocks', 'searchResults.html'),
      'utf-8'
    );

    mockFetch.mockResolvedValueOnce({
      ok: true,
      text: async () => mockHtml,
    } as any);

    const results = await searchLibrary('Foundation', 'local', 10);

    expect(mockFetch).toHaveBeenCalledTimes(1);
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('lookfor=Foundation'),
      expect.objectContaining({
        headers: expect.objectContaining({
          'User-Agent': expect.any(String),
        }),
      })
    );

    expect(results).toHaveLength(3);
    expect(results[0].title).toBe('Foundation');
  });

  it('should encode query parameters correctly', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      text: async () => '<html><body></body></html>',
    } as any);

    await searchLibrary('Test & Query', 'local', 10);

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('lookfor=Test%20%26%20Query'),
      expect.any(Object)
    );
  });

  it('should use correct searchSource parameter', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      text: async () => '<html><body></body></html>',
    } as any);

    await searchLibrary('test', 'all', 10);

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('searchSource=all'),
      expect.any(Object)
    );
  });

  it('should throw error on failed HTTP request', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
    } as any);

    await expect(searchLibrary('test', 'local', 10))
      .rejects
      .toThrow('HTTP error! status: 404');
  });

  it('should handle network errors', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    await expect(searchLibrary('test', 'local', 10))
      .rejects
      .toThrow('Network error');
  });

  it('should use default parameters', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      text: async () => '<html><body></body></html>',
    } as any);

    await searchLibrary('test');

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('searchSource=local'),
      expect.any(Object)
    );
  });
});
