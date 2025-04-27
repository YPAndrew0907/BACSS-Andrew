"""
Test to verify that no mock reviews are present in the output CSV.
"""
import os
import sys
import unittest
import pandas as pd
from pathlib import Path
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

class TestNoMockReviews(unittest.TestCase):
    """Test to verify that no mock reviews are present in the output CSV."""

    def test_no_mock_reviews_in_output(self):
        """Test that no review text starts with 'Mock review'."""
        sample_path = Path("data/output/sample/reviews_output_sample.csv")
        if sample_path.exists():
            self._check_file_for_mock_reviews(sample_path)
        
        full_path = Path("data/output/reviews_output.csv")
        if full_path.exists():
            self._check_file_for_mock_reviews(full_path)
        
        if not sample_path.exists() and not full_path.exists():
            print("No output files found to check for mock reviews.")
    
    def _check_file_for_mock_reviews(self, file_path):
        """Check a CSV file for mock reviews."""
        print(f"Checking {file_path} for mock reviews...")
        df = pd.read_csv(file_path)
        
        if 'review_text' not in df.columns:
            self.fail(f"Column 'review_text' not found in {file_path}")
        
        mock_reviews = df[df['review_text'].str.startswith('Mock review', na=False)]
        
        if not mock_reviews.empty:
            self.fail(f"Found {len(mock_reviews)} mock reviews in {file_path}")
        
        if 'reviewer_id' in df.columns:
            mock_users = df[df['reviewer_id'].str.startswith('mock_user', na=False)]
            
            if not mock_users.empty:
                self.fail(f"Found {len(mock_users)} mock user IDs in {file_path}")
        
        print(f"No mock reviews found in {file_path}")

if __name__ == '__main__':
    unittest.main()
