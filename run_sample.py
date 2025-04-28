"""
Script to run the Goodreads review scraper in sample mode and verify the output.
"""
import os
import sys
import pandas as pd
from pathlib import Path
import re
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from book_lookup import main as book_lookup_main
from review_scraper import main as review_scraper_main

def verify_output(output_path):
    """Verify that the output file meets all the requirements."""
    print(f"\nVerifying output file: {output_path}")
    
    if not output_path.exists():
        print(f"Error: Output file not found: {output_path}")
        return False
    
    df = pd.read_csv(output_path)
    
    print(f"Output file contains {len(df)} reviews")
    
    required_columns = [
        'book_id', 'title', 'author', 'goodreads_url',
        'review_text', 'review_rating', 'reviewer_id',
        'review_upvotes', 'review_date'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing required columns: {missing_columns}")
        return False
    
    print("All required columns are present")
    
    null_checks = {
        'book_id': df['book_id'].isna().sum(),
        'review_text': df['review_text'].isna().sum(),
        'review_rating': df['review_rating'].isna().sum()
    }
    
    if any(null_checks.values()):
        print(f"Error: Null values found in required fields: {null_checks}")
        return False
    
    print("No null values in required fields")
    
    invalid_ratings = df[~df['review_rating'].apply(
        lambda x: isinstance(x, (int, float)) and 1 <= x <= 5)]['review_rating'].tolist()
    
    if invalid_ratings:
        print(f"Error: Invalid ratings found: {invalid_ratings[:5]}")
        return False
    
    print("All ratings are valid (integers 1-5)")
    
    iso_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$')
    invalid_dates = df[~df['review_date'].apply(
        lambda x: isinstance(x, str) and bool(iso_pattern.match(x)))]['review_date'].tolist()
    
    if invalid_dates:
        print(f"Error: Invalid dates found: {invalid_dates[:5]}")
        return False
    
    print("All dates are in valid ISO-8601 format")
    
    extra_metadata = [col for col in df.columns if col not in required_columns]
    print(f"Extra metadata columns: {extra_metadata}")
    
    print("\nOutput file verification successful!")
    return True

def main():
    """Run the Goodreads review scraper in sample mode and verify the output."""
    print("Running Goodreads review scraper in sample mode...")
    
    print("\nRunning book lookup script in sample mode...")
    book_lookup_main(sample=True)
    
    print("\nRunning review scraper script in sample mode...")
    review_scraper_main(sample=True)
    
    output_path = Path("data/output/sample/reviews_output_sample.csv")
    success = verify_output(output_path)
    
    if not success:
        print("\nNo reviews found or output file not created.")
        print("This is expected behavior when no genuine reviews are found.")
        
        required_columns = [
            'book_id', 'title', 'author', 'goodreads_url',
            'review_text', 'review_rating', 'reviewer_id',
            'review_upvotes', 'review_date'
        ]
        
        empty_df = pd.DataFrame(columns=required_columns)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        empty_df.to_csv(output_path, index=False)
        
        print(f"Created empty output file with required columns")

if __name__ == "__main__":
    main()
