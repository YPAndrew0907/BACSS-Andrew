import os
import sys
import pandas as pd
from pathlib import Path
import logging

from src.book_lookup import GoodreadsBookLookup
from src.next_data_scraper import GoodreadsNextDataScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("full_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("full_scraper")

def main():
    print('Running full dataset scraper with __NEXT_DATA__ parser')
    
    input_file = 'data/input/goodreads_list.csv'
    output_dir = Path('data/output/full')
    cache_dir = Path('data/cache')
    
    os.makedirs(output_dir, exist_ok=True)
    
    print('\nStep 1: Looking up book URLs')
    lookup = GoodreadsBookLookup(cache_dir=cache_dir)
    books_with_urls = lookup.process_book_list(input_file)
    
    url_output_file = output_dir / 'goodreads_urls_full.csv'
    books_with_urls.to_csv(url_output_file, index=False)
    print(f'Saved {len(books_with_urls)} book URLs to {url_output_file}')
    
    print('\nStep 2: Scraping reviews using __NEXT_DATA__ parser')
    scraper = GoodreadsNextDataScraper(cache_dir=cache_dir)
    reviews_df = scraper.process_book_list(url_output_file)
    
    reviews_output_file = output_dir / 'reviews_output_full.csv'
    reviews_df.to_csv(reviews_output_file, index=False)
    print(f'Saved {len(reviews_df)} reviews to {reviews_output_file}')
    
    main_output_file = Path('data/output/reviews_output.csv')
    reviews_df.to_csv(main_output_file, index=False)
    print(f'Copied results to {main_output_file}')
    
    if len(reviews_df) > 0:
        print('\nSummary statistics:')
        total_books = len(books_with_urls)
        books_with_reviews = reviews_df['book_id'].nunique()
        print(f'Total books processed: {total_books}')
        print(f'Books with reviews: {books_with_reviews} ({books_with_reviews/total_books*100:.1f}%)')
        print(f'Total reviews: {len(reviews_df)}')
        if books_with_reviews > 0:
            print(f'Average reviews per book with reviews: {len(reviews_df)/books_with_reviews:.1f}')
    
    print('\nFull dataset scraping completed successfully!')

if __name__ == '__main__':
    main()
