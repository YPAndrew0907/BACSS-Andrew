"""
Unit tests for the review parsing functionality.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from review_scraper import GoodreadsReviewScraper
from bs4 import BeautifulSoup

class TestParseReview(unittest.TestCase):
    """Test the review parsing functionality."""

    def setUp(self):
        """Set up the test environment."""
        self.fixtures_dir = Path(__file__).parent / 'fixtures'
        self.cache_dir = Path(__file__).parent / 'cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        with open(self.fixtures_dir / 'review_page.html', 'r') as f:
            self.review_page_html = f.read()
        
        self.scraper = GoodreadsReviewScraper(cache_dir=self.cache_dir)
        
        self.soup = BeautifulSoup(self.review_page_html, 'html.parser')
        self.review_elements = self.soup.select('.review')

    def test_parse_review_text(self):
        """Test parsing the review text."""
        for review_element in self.review_elements:
            review_data = self.scraper.parse_review(review_element)
            self.assertIn('review_text', review_data)
            self.assertIsNotNone(review_data['review_text'])
            self.assertGreater(len(review_data['review_text']), 0)

    def test_parse_review_rating(self):
        """Test parsing the review rating."""
        for review_element in self.review_elements:
            review_data = self.scraper.parse_review(review_element)
            self.assertIn('review_rating', review_data)
            self.assertIsNotNone(review_data['review_rating'])
            self.assertIsInstance(review_data['review_rating'], int)
            self.assertGreaterEqual(review_data['review_rating'], 1)
            self.assertLessEqual(review_data['review_rating'], 5)

    def test_parse_reviewer_id(self):
        """Test parsing the reviewer ID."""
        for review_element in self.review_elements:
            review_data = self.scraper.parse_review(review_element)
            self.assertIn('reviewer_id', review_data)
            self.assertIsNotNone(review_data['reviewer_id'])
            self.assertGreater(len(review_data['reviewer_id']), 0)

    def test_parse_review_upvotes(self):
        """Test parsing the review upvotes."""
        for review_element in self.review_elements:
            review_data = self.scraper.parse_review(review_element)
            self.assertIn('review_upvotes', review_data)
            self.assertIsNotNone(review_data['review_upvotes'])
            self.assertIsInstance(review_data['review_upvotes'], int)
            self.assertGreaterEqual(review_data['review_upvotes'], 0)

    def test_parse_review_date(self):
        """Test parsing the review date."""
        for review_element in self.review_elements:
            review_data = self.scraper.parse_review(review_element)
            self.assertIn('review_date', review_data)
            self.assertIsNotNone(review_data['review_date'])
            
            iso_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$')
            self.assertTrue(iso_pattern.match(review_data['review_date']))
            
            try:
                datetime.fromisoformat(review_data['review_date'].replace('Z', '+00:00'))
            except ValueError:
                self.fail(f"Date {review_data['review_date']} is not in a valid ISO-8601 format")

    def test_parse_extra_metadata(self):
        """Test parsing extra metadata."""
        for review_element in self.review_elements:
            review_data = self.scraper.parse_review(review_element)
            
            self.assertIn('shelves', review_data)
            self.assertIsNotNone(review_data['shelves'])
            self.assertIsInstance(review_data['shelves'], list)
            
            self.assertIn('comment_count', review_data)
            self.assertIsNotNone(review_data['comment_count'])
            self.assertIsInstance(review_data['comment_count'], int)
            self.assertGreaterEqual(review_data['comment_count'], 0)

    def test_get_review_pages_count(self):
        """Test getting the number of review pages."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = self.review_page_html
            mock_get.return_value = mock_response
            
            book_url = "https://www.goodreads.com/book/show/5907.The_Hobbit"
            pages_count = self.scraper.get_review_pages_count(book_url)
            
            self.assertEqual(pages_count, 6)

    def test_get_reviews_from_page(self):
        """Test getting reviews from a page."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = self.review_page_html
            mock_get.return_value = mock_response
            
            book_url = "https://www.goodreads.com/book/show/5907.The_Hobbit"
            reviews = self.scraper.get_reviews_from_page(book_url, page=1)
            
            self.assertEqual(len(reviews), 2)
            
            first_review = reviews[0]
            self.assertEqual(first_review['reviewer_name'], "BookLover42")
            self.assertEqual(first_review['reviewer_id'], "12345")
            self.assertEqual(first_review['review_rating'], 5)
            self.assertEqual(first_review['review_upvotes'], 42)
            self.assertEqual(first_review['comment_count'], 5)
            self.assertIn("This is an amazing book!", first_review['review_text'])
            self.assertIn("fantasy", first_review['shelves'])
            self.assertIn("classics", first_review['shelves'])
            self.assertIn("favorites", first_review['shelves'])

if __name__ == '__main__':
    unittest.main()
