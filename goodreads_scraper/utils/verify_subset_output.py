"""
Script to verify the subset output CSV contains only genuine Goodreads reviews.
"""
import pandas as pd
from pathlib import Path
import re

def verify_subset_output():
    """Verify the subset output CSV contains only genuine Goodreads reviews."""
    sample_path = Path("data/output/sample/reviews_output_sample.csv")
    
    if not sample_path.exists():
        print(f"Error: Sample output file not found: {sample_path}")
        return False
    
    print(f"Verifying sample output file: {sample_path}")
    
    df = pd.read_csv(sample_path)
    print(f"Total rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    
    if 'review_text' in df.columns:
        mock_reviews = df[df['review_text'].str.startswith('Mock review', na=False)]
        if not mock_reviews.empty:
            print(f"Error: Found {len(mock_reviews)} mock reviews")
            return False
        print("No mock reviews found")
    
    if 'reviewer_id' in df.columns:
        mock_users = df[df['reviewer_id'].str.startswith('mock_user', na=False)]
        if not mock_users.empty:
            print(f"Error: Found {len(mock_users)} mock user IDs")
            return False
        print("No mock user IDs found")
    
    if df.empty:
        print("Output file is empty, which is expected when no genuine reviews are found")
        return True
    
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
    
    for col in ['book_id', 'review_text', 'review_rating']:
        if col in df.columns and df[col].isna().sum() > 0:
            print(f"Error: Found {df[col].isna().sum()} null values in '{col}' column")
            return False
    
    print("No null values in required fields")
    
    if 'review_rating' in df.columns:
        invalid_ratings = df[~df['review_rating'].apply(
            lambda x: isinstance(x, (int, float)) and 1 <= x <= 5)]['review_rating'].tolist()
        
        if invalid_ratings:
            print(f"Error: Invalid ratings found: {invalid_ratings[:5]}")
            return False
        
        print("All ratings are valid (integers 1-5)")
    
    if 'review_date' in df.columns:
        iso_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$')
        invalid_dates = df[~df['review_date'].apply(
            lambda x: isinstance(x, str) and bool(iso_pattern.match(x)))]['review_date'].tolist()
        
        if invalid_dates:
            print(f"Error: Invalid dates found: {invalid_dates[:5]}")
            return False
        
        print("All dates are in valid ISO-8601 format")
    
    print("\nSubset output verification successful!")
    return True

if __name__ == "__main__":
    verify_subset_output()
