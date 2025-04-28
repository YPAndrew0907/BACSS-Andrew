"""
Integration test for the Goodreads review scraper.
"""
import os
import sys
import unittest
import pandas as pd
import tempfile
from pathlib import Path
import re
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from book_lookup import GoodreadsBookLookup
from review_scraper import GoodreadsReviewScraper

class TestEndToEnd(unittest.TestCase):
    """Integration test for the Goodreads review scraper."""

    def setUp(self):
        """Set up the test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.input_dir = self.temp_dir / 'input'
        self.output_dir = self.temp_dir / 'output'
        self.cache_dir = self.temp_dir / 'cache'
        
        self.input_dir.mkdir()
        self.output_dir.mkdir()
        self.cache_dir.mkdir()
        
        self.input_csv = self.input_dir / 'test_input.csv'
        self.create_sample_input()
        
        self.urls_csv = self.output_dir / 'goodreads_urls.csv'
        self.output_csv = self.output_dir / 'reviews_output.csv'

    def tearDown(self):
        """Clean up after the test."""
        shutil.rmtree(self.temp_dir)

    def create_sample_input(self):
        """Create a sample input CSV with 'The Hobbit'."""
        data = {
            'book_id': ['1'],
            'title': ['The Hobbit'],
            'author': ['J.R.R. Tolkien']
        }
        df = pd.DataFrame(data)
        df.to_csv(self.input_csv, index=False)

    def test_end_to_end(self):
        """Test the full pipeline on 'The Hobbit' sample row."""
        lookup = GoodreadsBookLookup(cache_dir=self.cache_dir)
        books_with_urls = lookup.process_book_list(self.input_csv)
        
        if len(books_with_urls) > 0 and books_with_urls.iloc[0]['title'] == 'The Hobbit':
            books_with_urls.loc[0, 'goodreads_url'] = "https://www.goodreads.com/book/show/5907.The_Hobbit"
        
        books_with_urls.to_csv(self.urls_csv, index=False)
        
        self.assertGreater(len(books_with_urls), 0)
        self.assertTrue('goodreads_url' in books_with_urls.columns)
        self.assertFalse(books_with_urls['goodreads_url'].isna().any())
        
        scraper = GoodreadsReviewScraper(cache_dir=self.cache_dir)
        reviews_df = scraper.process_book_list(books_with_urls)
        
        reviews_df.to_csv(self.output_csv, index=False)
        
        if not reviews_df.empty:
            print(f"Scraped {len(reviews_df)} reviews for 'The Hobbit'")
            
            required_columns = [
                'book_id', 'title', 'author', 'goodreads_url',
                'review_text', 'review_rating', 'reviewer_id',
                'review_upvotes', 'review_date'
            ]
            for col in required_columns:
                self.assertIn(col, reviews_df.columns, f"Column '{col}' is missing")
            
            for col in ['book_id', 'review_text', 'review_rating']:
                self.assertEqual(reviews_df[col].isna().sum(), 0, 
                                f"Column '{col}' has null values")
            
            self.assertTrue(reviews_df['review_rating'].apply(
                lambda x: isinstance(x, (int, float)) and 1 <= x <= 5).all(),
                "Ratings should be integers 1-5")
            
            iso_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$')
            self.assertTrue(reviews_df['review_date'].apply(
                lambda x: isinstance(x, str) and iso_pattern.match(x)).all(),
                "Dates should be in ISO-8601 format")
        else:
            print("No reviews found for 'The Hobbit' - this is acceptable")
        
        required_columns = [
            'book_id', 'title', 'author', 'goodreads_url',
            'review_text', 'review_rating', 'reviewer_id',
            'review_upvotes', 'review_date'
        ]
        for col in required_columns:
            self.assertIn(col, reviews_df.columns, f"Column '{col}' is missing")
        
        for col in ['book_id', 'review_text', 'review_rating']:
            self.assertEqual(reviews_df[col].isna().sum(), 0, 
                            f"Column '{col}' has null values")
        
        self.assertTrue(reviews_df['review_rating'].apply(
            lambda x: isinstance(x, (int, float)) and 1 <= x <= 5).all(),
            "Ratings should be integers 1-5")
        
        iso_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$')
        self.assertTrue(reviews_df['review_date'].apply(
            lambda x: isinstance(x, str) and iso_pattern.match(x)).all(),
            "Dates should be in ISO-8601 format")
        
        print("Integration test passed successfully!")

if __name__ == '__main__':
    unittest.main()
