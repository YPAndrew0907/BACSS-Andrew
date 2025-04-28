"""
Unit tests for the book matching functionality.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from book_lookup import GoodreadsBookLookup

class TestMatching(unittest.TestCase):
    """Test the book matching functionality."""

    def setUp(self):
        """Set up the test environment."""
        self.fixtures_dir = Path(__file__).parent / 'fixtures'
        self.cache_dir = Path(__file__).parent / 'cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        with open(self.fixtures_dir / 'search_results.html', 'r') as f:
            self.search_results_html = f.read()
        
        self.lookup = GoodreadsBookLookup(cache_dir=self.cache_dir)

    def test_find_best_match_exact(self):
        """Test finding the best match with exact title and author."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = self.search_results_html
            mock_get.return_value = mock_response
            
            title = "The Hobbit"
            author = "J.R.R. Tolkien"
            search_results = self.lookup.search_book(title, author)
            
            best_match = self.lookup.find_best_match(title, author, search_results)
            
            self.assertIsNotNone(best_match)
            self.assertEqual(best_match['url'], "https://www.goodreads.com/book/show/5907.The_Hobbit")
            self.assertEqual(best_match['title'], "The Hobbit")
            self.assertEqual(best_match['author'], "J.R.R. Tolkien")

    def test_find_best_match_fuzzy(self):
        """Test finding the best match with fuzzy title and author."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = self.search_results_html
            mock_get.return_value = mock_response
            
            title = "The Hobit"  # Misspelled
            author = "J. R. R. Tolkien"  # Different spacing
            search_results = self.lookup.search_book(title, author)
            
            best_match = self.lookup.find_best_match(title, author, search_results)
            
            self.assertIsNotNone(best_match)
            self.assertEqual(best_match['url'], "https://www.goodreads.com/book/show/5907.The_Hobbit")
            self.assertEqual(best_match['title'], "The Hobbit")
            self.assertEqual(best_match['author'], "J.R.R. Tolkien")

    def test_find_best_match_threshold(self):
        """Test that matches below the threshold are rejected."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = self.search_results_html
            mock_get.return_value = mock_response
            
            title = "Lord of the Rings"
            author = "J.R.R. Tolkien"
            search_results = self.lookup.search_book(title, author)
            
            best_match = self.lookup.find_best_match(title, author, search_results)
            
            self.assertIsNone(best_match)

    def test_verify_title_and_author(self):
        """Test that both title and author are verified."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = self.search_results_html
            mock_get.return_value = mock_response
            
            title = "The Hobbit"
            author = "George R.R. Martin"
            search_results = self.lookup.search_book(title, author)
            
            best_match = self.lookup.find_best_match(title, author, search_results)
            
            self.assertIsNone(best_match)

if __name__ == '__main__':
    unittest.main()
