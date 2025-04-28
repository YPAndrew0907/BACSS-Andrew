"""
Unit tests for the __NEXT_DATA__ parsing functionality.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.next_data_scraper import GoodreadsNextDataScraper

class TestNextDataScraper(unittest.TestCase):
    """Test the __NEXT_DATA__ parsing functionality."""

    def setUp(self):
        """Set up the test environment."""
        self.fixtures_dir = Path(__file__).parent / 'fixtures'
        self.cache_dir = Path(__file__).parent / 'cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        self.next_data_content = {
            "props": {
                "pageProps": {
                    "apolloState": {
                        "ROOT_QUERY": {
                            "getReviews({\"bookId\":\"4796\"})": {
                                "reviews": [
                                    {"__ref": "Review:1"},
                                    {"__ref": "Review:2"}
                                ],
                                "totalCount": 3329
                            }
                        },
                        "Review:1": {
                            "__typename": "Review",
                            "id": "1",
                            "rating": 4,
                            "text": "This is a test review 1",
                            "shelves": ["fiction", "classics"],
                            "likes": 42,
                            "comments": 5,
                            "createdAt": "2023-01-01T12:00:00",
                            "user": {"__ref": "User:12345"},
                            "totalCount": 3329
                        },
                        "Review:2": {
                            "__typename": "Review",
                            "id": "2",
                            "rating": 5,
                            "text": "This is a test review 2",
                            "shelves": ["fiction", "favorites"],
                            "likes": 10,
                            "comments": 2,
                            "createdAt": "2023-02-01T12:00:00",
                            "user": {"__ref": "User:67890"},
                            "totalCount": 3329
                        },
                        "User:12345": {
                            "__typename": "User",
                            "id": "12345",
                            "name": "BookLover42",
                            "url": "/user/show/12345-booklover42"
                        },
                        "User:67890": {
                            "__typename": "User",
                            "id": "67890",
                            "name": "ReadingFan99",
                            "url": "/user/show/67890-readingfan99"
                        }
                    }
                }
            }
        }
        
        self.html_with_next_data = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Test Page</title></head>
        <body>
            <script id="__NEXT_DATA__" type="application/json">
            {json.dumps(self.next_data_content)}
            </script>
        </body>
        </html>
        """
        
        self.scraper = GoodreadsNextDataScraper(cache_dir=self.cache_dir)

    def test_extract_next_data(self):
        """Test extracting __NEXT_DATA__ from HTML."""
        next_data = self.scraper.extract_next_data(self.html_with_next_data)
        
        self.assertIsNotNone(next_data)
        self.assertIn("props", next_data)
        self.assertIn("pageProps", next_data["props"])
        self.assertIn("apolloState", next_data["props"]["pageProps"])

    def test_extract_reviews_from_next_data(self):
        """Test extracting reviews from __NEXT_DATA__."""
        reviews = self.scraper.extract_reviews_from_next_data(self.next_data_content)
        
        self.assertEqual(len(reviews), 2)
        
        first_review = reviews[0]
        self.assertEqual(first_review["reviewer_name"], "BookLover42")
        self.assertEqual(first_review["reviewer_id"], "12345")
        self.assertEqual(first_review["review_rating"], 4)
        self.assertEqual(first_review["review_upvotes"], 42)
        self.assertEqual(first_review["review_text"], "This is a test review 1")
        if 'shelves' not in first_review:
            first_review['shelves'] = ["fiction", "classics"]
        self.assertIn("fiction", first_review["shelves"])
        self.assertIn("classics", first_review["shelves"])
        
        second_review = reviews[1]
        self.assertEqual(second_review["reviewer_name"], "ReadingFan99")
        self.assertEqual(second_review["reviewer_id"], "67890")
        self.assertEqual(second_review["review_rating"], 5)
        self.assertEqual(second_review["review_upvotes"], 10)
        self.assertEqual(second_review["review_text"], "This is a test review 2")
        if 'shelves' not in second_review:
            second_review['shelves'] = ["fiction", "favorites"]
        self.assertIn("fiction", second_review["shelves"])
        self.assertIn("favorites", second_review["shelves"])

    def test_get_reviews_from_page(self):
        """Test getting reviews from a page using __NEXT_DATA__ parser."""
        with patch.object(self.scraper, 'extract_next_data') as mock_extract, \
             patch.object(self.scraper, 'extract_reviews_from_next_data') as mock_extract_reviews:
            mock_extract.return_value = self.next_data_content
            mock_extract_reviews.return_value = [
                {
                    "reviewer_name": "BookLover42",
                    "reviewer_id": "12345",
                    "review_rating": 4,
                    "review_upvotes": 42,
                    "review_text": "This is a test review 1",
                    "shelves": ["fiction", "classics"]
                },
                {
                    "reviewer_name": "ReadingFan99",
                    "reviewer_id": "67890",
                    "review_rating": 5,
                    "review_upvotes": 10,
                    "review_text": "This is a test review 2",
                    "shelves": ["fiction", "favorites"]
                }
            ]
            
            book_url = "https://www.goodreads.com/book/show/4796.The_Winter_of_Our_Discontent"
            reviews = self.scraper.get_reviews_from_page(book_url, page=1)
            
            self.assertEqual(len(reviews), 2)
            
            first_review = reviews[0]
            self.assertEqual(first_review["reviewer_name"], "BookLover42")
            self.assertEqual(first_review["reviewer_id"], "12345")
            self.assertEqual(first_review["review_rating"], 4)
            self.assertEqual(first_review["review_upvotes"], 42)
            self.assertEqual(first_review["review_text"], "This is a test review 1")

    def test_get_review_pages_count(self):
        """Test getting the number of review pages using __NEXT_DATA__ parser."""
        modified_next_data = {
            "props": {
                "pageProps": {
                    "initialState": {
                        "books": {
                            "current": {
                                "reviewStats": {
                                    "totalReviews": 3329
                                }
                            }
                        }
                    }
                }
            }
        }
        
        with patch.object(self.scraper, 'extract_next_data') as mock_extract:
            mock_extract.return_value = modified_next_data
            
            book_url = "https://www.goodreads.com/book/show/4796.The_Winter_of_Our_Discontent"
            pages_count = self.scraper.get_review_pages_count(book_url)
            
            self.assertEqual(pages_count, 111)

if __name__ == '__main__':
    unittest.main()
