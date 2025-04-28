# Goodreads Review Scraper

A robust Python-based web scraper for extracting book reviews from Goodreads.

## Overview

This project provides a comprehensive solution for scraping book reviews from Goodreads. It takes a CSV file with book information (ID, title, author) and produces a CSV file with detailed review data including review text, ratings, reviewer information, and more.

## Features

- Compliant with Goodreads' `robots.txt` with appropriate rate limiting
- Robust error handling with retry and back-off mechanisms
- High-fidelity book matching using fuzzy string scoring
- Comprehensive review extraction including metadata
- Caching to reduce redundant requests and ease debugging

## Project Structure

```
/
├── src/                     # Core functionality
│   ├── book_lookup.py       # Book search and URL matching
│   ├── review_scraper.py    # Review extraction using HTML parsing
│   └── next_data_scraper.py # Review extraction using __NEXT_DATA__
├── notebooks/               # Jupyter notebooks
│   └── demo.ipynb           # Demonstration notebook
├── data/                    # Data directory
│   ├── input/               # Input data directory
│   │   └── goodreads_list.csv  # List of books to scrape
│   ├── output/              # Output data directory
│   │   └── reviews_output.csv  # Scraped reviews
│   └── cache/               # Cache directory for HTTP responses
├── reports/                 # Reports directory
│   └── methodology.md       # Methodology documentation
├── tests/                   # Test directory
└── *.py                     # Runner and utility scripts at root level
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/goodreads-scraper.git
cd goodreads-scraper

# Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install requests beautifulsoup4 rapidfuzz pandas tqdm tenacity pytest ruff
```

## Usage

### Basic Usage

```bash
# Run the book lookup to find Goodreads URLs
python book_lookup.py

# Run the review scraper to extract reviews
python review_scraper.py
```

### Advanced Usage

```bash
# Run with sample data
python book_lookup.py --sample
python review_scraper.py --sample

# Run with verbose logging
python review_scraper.py --verbose

# Scrape a single book
python review_scraper.py --single-book "https://www.goodreads.com/book/show/1885.Pride_and_Prejudice"

# Limit the number of pages to scrape
python review_scraper.py --max-pages 5
```

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_matching.py
```

## Troubleshooting

### Rate Limiting and Anti-Scraping Measures

Goodreads implements various anti-scraping measures that may affect the scraper's performance:

1. **Adjusting Rate Limits**: If you encounter 429 (Too Many Requests) errors, you can modify the rate limiting in `src/review_scraper.py`:

   ```python
   # Find the _rate_limit method in GoodreadsReviewScraper class
   def _rate_limit(self):
       """Implement rate limiting to respect robots.txt."""
       time.sleep(2)  # Increase this value (e.g., to 3-5 seconds) if you're being rate-limited
   ```

2. **Customizing User-Agent**: If you're being blocked, try changing the User-Agent in `src/review_scraper.py`:

   ```python
   # Find the headers in the __init__ method of GoodreadsReviewScraper class
   self.headers = {
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
       # Try different User-Agent strings or rotate between multiple
   }
   ```

3. **JavaScript-Loaded Content**: Goodreads loads reviews dynamically using JavaScript, which the scraper cannot access directly. Consider:
   - Using Selenium or Playwright for a headless browser approach
   - Implementing a direct API endpoint solution if available

4. **CAPTCHA Handling**: If you encounter CAPTCHAs:
   - Implement longer delays between requests
   - Use a more diverse set of User-Agent strings
   - Consider using a proxy rotation service

### Common Issues

1. **No Reviews Found**: This is often due to JavaScript-loaded content. The scraper logs will indicate if this is the case.

2. **Matching Issues**: If the scraper is not finding the correct book URLs, you can adjust the similarity threshold in `src/book_lookup.py`:

   ```python
   # Find the SIMILARITY_THRESHOLD constant
   SIMILARITY_THRESHOLD = 70  # Decrease this value for more lenient matching
   ```

3. **Memory Issues**: If you're scraping a large number of books, you might encounter memory issues. Consider:
   - Processing books in smaller batches
   - Implementing checkpointing to save progress periodically

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Requests](https://requests.readthedocs.io/) for HTTP requests
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [RapidFuzz](https://github.com/maxbachmann/RapidFuzz) for fuzzy string matching
- [Pandas](https://pandas.pydata.org/) for data manipulation
