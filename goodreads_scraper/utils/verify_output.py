"""
Verification script for the Goodreads review scraper output.

This script checks that:
1. The output CSV file exists
2. The output contains genuine reviews (not mock reviews)
3. All required fields are present
4. Reviews are present for multiple books
"""
import os
import sys
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("output_verification.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("output_verification")

def verify_output(output_file: str = 'data/output/reviews_output.csv') -> bool:
    """
    Verify the output CSV file.
    
    Args:
        output_file: Path to the output CSV file
        
    Returns:
        True if verification passes, False otherwise
    """
    output_path = Path(output_file)
    
    if not output_path.exists():
        logger.error(f"Output file not found: {output_path}")
        return False
    
    logger.info(f"Output file found: {output_path}")
    
    try:
        reviews_df = pd.read_csv(output_path)
        logger.info(f"Successfully read {len(reviews_df)} reviews from {output_path}")
    except Exception as e:
        logger.error(f"Error reading output file: {e}")
        return False
    
    if reviews_df.empty:
        logger.error("Output file is empty")
        return False
    
    required_fields = [
        'book_id', 'title', 'author', 'goodreads_url',
        'review_text', 'review_rating', 'reviewer_id', 'reviewer_name',
        'review_upvotes', 'review_date'
    ]
    
    missing_fields = [field for field in required_fields if field not in reviews_df.columns]
    
    if missing_fields:
        logger.error(f"Missing required fields: {missing_fields}")
        return False
    
    logger.info(f"All required fields are present: {required_fields}")
    
    mock_reviews = reviews_df[reviews_df['review_text'].str.contains('Mock review', na=False)]
    
    if not mock_reviews.empty:
        logger.error(f"Found {len(mock_reviews)} mock reviews")
        return False
    
    logger.info("No mock reviews found")
    
    empty_reviews = reviews_df[reviews_df['review_text'].isna() | (reviews_df['review_text'] == '')]
    
    if not empty_reviews.empty:
        logger.warning(f"Found {len(empty_reviews)} reviews with empty text")
    
    unique_books = reviews_df['book_id'].nunique()
    
    if unique_books < 2:
        logger.warning(f"Found reviews for only {unique_books} book(s)")
    else:
        logger.info(f"Found reviews for {unique_books} books")
    
    for field in ['book_id', 'review_text', 'review_rating']:
        null_count = reviews_df[field].isna().sum()
        if null_count > 0:
            logger.warning(f"Found {null_count} null values in '{field}' column")
    
    if 'review_rating' in reviews_df.columns:
        invalid_ratings = reviews_df[
            ~reviews_df['review_rating'].isna() & 
            ~reviews_df['review_rating'].isin([1, 2, 3, 4, 5])
        ]
        
        if not invalid_ratings.empty:
            logger.warning(f"Found {len(invalid_ratings)} reviews with invalid ratings")
    
    logger.info("\nSummary Statistics:")
    logger.info(f"Total reviews: {len(reviews_df)}")
    logger.info(f"Unique books: {unique_books}")
    logger.info(f"Unique reviewers: {reviews_df['reviewer_id'].nunique()}")
    
    if 'review_rating' in reviews_df.columns:
        avg_rating = reviews_df['review_rating'].mean()
        logger.info(f"Average rating: {avg_rating:.2f}")
    
    logger.info("\nSample Reviews:")
    sample_size = min(5, len(reviews_df))
    
    for _, row in reviews_df.sample(sample_size).iterrows():
        logger.info(f"\nBook: {row.get('title', 'Unknown')} by {row.get('author', 'Unknown')}")
        logger.info(f"Review by {row.get('reviewer_name', 'Unknown')} (ID: {row.get('reviewer_id', 'Unknown')})")
        logger.info(f"Rating: {row.get('review_rating', 'Unknown')}")
        
        review_text = row.get('review_text', '')
        if review_text:
            preview = review_text[:100] + '...' if len(review_text) > 100 else review_text
            logger.info(f"Text: {preview}")
    
    logger.info("\nVerification completed successfully!")
    return True

def main():
    """Main function to run the verification script."""
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = 'data/output/reviews_output.csv'
    
    logger.info(f"Verifying output file: {output_file}")
    
    success = verify_output(output_file)
    
    if success:
        logger.info("Verification passed!")
        return 0
    else:
        logger.error("Verification failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
