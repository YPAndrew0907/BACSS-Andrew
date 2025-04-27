"""
Script to run the full Goodreads review scraper for all books in the input file.
"""
import os
import sys
import pandas as pd
from pathlib import Path
import time
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from book_lookup import GoodreadsBookLookup
from review_scraper import GoodreadsReviewScraper

def main():
    """Run the full Goodreads review scraper for all books in the input file."""
    print("Starting full Goodreads review scraper...")
    start_time = time.time()
    
    logging.basicConfig(
        filename='full_scraper.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('full_scraper')
    
    input_path = Path("data/input/goodreads_list.csv")
    urls_path = Path("data/output/goodreads_urls.csv")
    output_path = Path("data/output/reviews_output.csv")
    cache_dir = Path("data/cache")
    
    cache_dir.mkdir(exist_ok=True)
    
    logger.info("Step 1: Processing book list to get Goodreads URLs")
    print("Step 1: Processing book list to get Goodreads URLs...")
    
    lookup = GoodreadsBookLookup(cache_dir=cache_dir)
    books_with_urls = lookup.process_book_list(input_path)
    
    books_with_urls.to_csv(urls_path, index=False)
    
    logger.info(f"Found URLs for {len(books_with_urls)} books")
    print(f"Found URLs for {len(books_with_urls)} books")
    
    logger.info("Step 2: Scraping reviews for each book")
    print("Step 2: Scraping reviews for each book...")
    
    scraper = GoodreadsReviewScraper(cache_dir=cache_dir)
    reviews_df = scraper.process_book_list(books_with_urls)
    
    reviews_df.to_csv(output_path, index=False)
    
    elapsed_time = time.time() - start_time
    logger.info(f"Scraping completed in {elapsed_time:.2f} seconds")
    logger.info(f"Scraped {len(reviews_df)} reviews for {len(books_with_urls)} books")
    
    print(f"\nScraping completed in {elapsed_time:.2f} seconds")
    print(f"Scraped {len(reviews_df)} reviews for {len(books_with_urls)} books")
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    main()
