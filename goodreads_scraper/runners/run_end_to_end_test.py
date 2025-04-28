import os
import sys
import pandas as pd
from pathlib import Path

from src.book_lookup import GoodreadsBookLookup
from src.next_data_scraper import GoodreadsNextDataScraper

def main():
    print('Running end-to-end test with __NEXT_DATA__ parser')
    
    input_file = 'data/input/test_book.csv'
    output_dir = Path('data/output/test')
    cache_dir = Path('data/cache')
    
    os.makedirs(output_dir, exist_ok=True)
    
    print('\nStep 1: Looking up book URLs')
    lookup = GoodreadsBookLookup(cache_dir=cache_dir)
    books_with_urls = lookup.process_book_list(input_file)
    
    url_output_file = output_dir / 'goodreads_urls_test.csv'
    books_with_urls.to_csv(url_output_file, index=False)
    print(f'Saved {len(books_with_urls)} book URLs to {url_output_file}')
    
    print('\nStep 2: Scraping reviews using __NEXT_DATA__ parser')
    scraper = GoodreadsNextDataScraper(cache_dir=cache_dir)
    reviews_df = scraper.process_book_list(url_output_file, max_pages=2)
    
    reviews_output_file = output_dir / 'reviews_output_test.csv'
    reviews_df.to_csv(reviews_output_file, index=False)
    print(f'Saved {len(reviews_df)} reviews to {reviews_output_file}')
    
    if len(reviews_df) > 0:
        print('\nSample of reviews:')
        sample = reviews_df.head(3)
        for _, row in sample.iterrows():
            print(f'\nReview by {row.get("reviewer_name", "Unknown")} (ID: {row.get("reviewer_id", "Unknown")})')
            print(f'Rating: {row.get("review_rating", "Unknown")}')
            review_text = row.get("review_text", "")
            if review_text:
                print(f'Text: {review_text[:100]}...' if len(review_text) > 100 else f'Text: {review_text}')
    
    print('\nEnd-to-end test completed successfully!')

if __name__ == '__main__':
    main()
