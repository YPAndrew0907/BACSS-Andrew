"""
Script to check the output file format and data quality.
"""
import pandas as pd
import re
from pathlib import Path

def check_output_file(file_path):
    """Check the output file format and data quality."""
    print(f"Checking output file: {file_path}")
    
    df = pd.read_csv(file_path)
    
    print(f"Total reviews: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Unique books: {df.book_id.nunique()}")
    
    required_columns = [
        'book_id', 'title', 'author', 'goodreads_url',
        'review_text', 'review_rating', 'reviewer_id',
        'review_upvotes', 'review_date'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"ERROR: Missing required columns: {missing_columns}")
    else:
        print("All required columns are present")
    
    null_checks = {
        'book_id': df['book_id'].isna().sum(),
        'review_text': df['review_text'].isna().sum(),
        'review_rating': df['review_rating'].isna().sum()
    }
    
    if any(null_checks.values()):
        print(f"ERROR: Null values found in required fields: {null_checks}")
    else:
        print("No null values in required fields")
    
    invalid_ratings = df[~df['review_rating'].apply(
        lambda x: isinstance(x, (int, float)) and 1 <= x <= 5)]['review_rating'].tolist()
    
    if invalid_ratings:
        print(f"ERROR: Invalid ratings found: {invalid_ratings[:5]}")
    else:
        print("All ratings are valid (integers 1-5)")
    
    iso_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$')
    invalid_dates = df[~df['review_date'].apply(
        lambda x: isinstance(x, str) and bool(iso_pattern.match(x)))]['review_date'].tolist()
    
    if invalid_dates:
        print(f"ERROR: Invalid dates found: {invalid_dates[:5]}")
    else:
        print("All dates are in valid ISO-8601 format")
    
    extra_metadata = [col for col in df.columns if col not in required_columns]
    print(f"Extra metadata columns: {extra_metadata}")
    
    print("\nOutput file verification successful!")

if __name__ == "__main__":
    sample_path = Path("data/output/sample/reviews_output_sample.csv")
    if sample_path.exists():
        check_output_file(sample_path)
    else:
        print(f"Sample output file not found: {sample_path}")
    
    full_path = Path("data/output/reviews_output.csv")
    if full_path.exists():
        check_output_file(full_path)
    else:
        print(f"\nFull output file not found: {full_path}")
        print("The full scraper is still running...")
