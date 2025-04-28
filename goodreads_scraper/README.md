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
goodreads_scraper/
├── __init__.py                  # Package initialization
├── __main__.py                  # Entry point for running as a module
├── core/                        # Core functionality
│   ├── __init__.py
│   ├── book_lookup.py           # Book search and URL matching
│   ├── review_scraper.py        # Review extraction using HTML parsing
│   └── next_data_scraper.py     # Review extraction using __NEXT_DATA__
├── runners/                     # Runner scripts
│   ├── __init__.py
│   ├── run_full_scraper.py      # Run the full scraper pipeline
│   ├── run_sample.py            # Run with sample data
│   └── run_full_dataset.py      # Run with full dataset
├── utils/                       # Utility scripts
│   ├── __init__.py
│   ├── check_cached_reviews.py  # Check cached review pages
│   ├── check_empty_reviews.py   # Check for empty reviews
│   ├── check_output.py          # Check output files
│   ├── verify_output.py         # Verify output data
│   └── generate_report.py       # Generate final report
└── tests/                       # Test suite
    ├── __init__.py
    ├── test_*.py                # Test files
    └── fixtures/                # Test fixtures
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
pip install -e .
```

## Usage

### Basic Usage

```bash
# Run the full scraper
python -m goodreads_scraper full

# Run with sample data
python -m goodreads_scraper sample

# Generate a final report
python -m goodreads_scraper report
```

### Advanced Usage

You can also use the individual modules directly:

```python
from goodreads_scraper.core.book_lookup import GoodreadsBookLookup
from goodreads_scraper.core.review_scraper import GoodreadsReviewScraper

# Look up book URLs
lookup = GoodreadsBookLookup()
books_with_urls = lookup.process_book_list("data/input/goodreads_list.csv")

# Scrape reviews
scraper = GoodreadsReviewScraper()
reviews_df = scraper.process_book_list(books_with_urls)
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

1. **Adjusting Rate Limits**: If you encounter 429 (Too Many Requests) errors, you can modify the rate limiting in `core/review_scraper.py`:

   ```python
   # Find the _rate_limit method in GoodreadsReviewScraper class
   def _rate_limit(self):
       """Implement rate limiting to respect robots.txt."""
       time.sleep(2)  # Increase this value (e.g., to 3-5 seconds) if you're being rate-limited
   ```

2. **Customizing User-Agent**: If you're being blocked, try changing the User-Agent in `core/review_scraper.py`:

   ```python
   # Find the headers in the __init__ method of GoodreadsReviewScraper class
   self.headers = {
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
       # Try different User-Agent strings or rotate between multiple
   }
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
