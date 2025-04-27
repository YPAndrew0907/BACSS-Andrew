# Goodreads Review Scraper: Methodology

This document outlines the methodology used in the Goodreads review scraper, covering matching logic, pagination strategy, challenges encountered, and mitigations implemented.

## Matching Logic

The scraper uses fuzzy string matching to find the correct book page on Goodreads:

1. **Search Process**: For each book in the input CSV, the scraper sends a search query to Goodreads combining both title and author.
2. **Fuzzy Matching**: Using RapidFuzz 3.0+, the scraper calculates similarity scores between:
   - Original title and search result titles (60% weight)
   - Original author and search result authors (40% weight)
3. **Threshold Application**: Only matches with a combined similarity score ≥ 85 are considered valid.
4. **Verification**: Both title and author are verified to ensure the correct book is identified.

## Pagination Strategy

The scraper handles review pagination through the following approach:

1. **Page Count Detection**: The scraper first determines the total number of review pages by examining the pagination elements on the first reviews page.
2. **Iterative Extraction**: It then iterates through each page, extracting all reviews while maintaining the rate limit.
3. **Structured Collection**: Reviews from all pages are aggregated into a unified data structure, preserving the relationship to the source book.

## Challenges & Mitigations

Several challenges were encountered during development:

1. **Rate Limiting**:
   - **Challenge**: Goodreads implements rate limiting to prevent scraping.
   - **Mitigation**: Implemented a 2-second delay between requests and exponential backoff for 429 responses.

2. **CAPTCHA Detection**:
   - **Challenge**: Frequent requests may trigger CAPTCHA challenges.
   - **Mitigation**: The scraper detects CAPTCHA presence in responses, logs occurrences, and skips after 3 retries.

3. **HTML Structure Variations**:
   - **Challenge**: Goodreads' HTML structure may vary across different book pages.
   - **Mitigation**: Implemented robust parsing with multiple fallback selectors and error handling.

4. **Data Quality**:
   - **Challenge**: Some reviews may have missing fields or inconsistent formats.
   - **Mitigation**: Implemented data validation and cleaning to ensure output consistency.

5. **Performance Optimization**:
   - **Challenge**: Scraping all reviews for many books is time-consuming.
   - **Mitigation**: Implemented response caching to `/data/cache/` to avoid redundant requests during development and debugging.

## Gen-AI Usage

No generative AI tools were used in the development of the core scraping logic. The implementation relies on established libraries and standard web scraping techniques.

---

## Appendix: AI Prompts

While no AI was used for generating code, the following prompts could be useful for troubleshooting or extending the scraper:

1. **Debugging Selector Issues**:
   ```
   The following HTML structure from Goodreads has changed and my CSS selector no longer works:
   [HTML snippet]
   
   My current selector is: [selector]
   What would be a more robust selector to extract the review text?
   ```

2. **Optimizing Rate Limiting**:
   ```
   I'm implementing rate limiting for a Goodreads scraper. Currently using a fixed 2-second delay.
   What would be a more adaptive approach that respects the site's limits while maximizing throughput?
   ```

3. **Improving Fuzzy Matching**:
   ```
   I'm using RapidFuzz with a threshold of 85 for matching book titles and authors.
   Here are examples of matches that failed: [examples]
   How can I improve my matching algorithm while maintaining precision?
   ```
