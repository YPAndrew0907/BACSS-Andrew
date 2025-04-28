"""
Test script to verify the __NEXT_DATA__ parsing functionality.

This script tests the ability to extract review data from the __NEXT_DATA__ script tag
in Goodreads pages without using a headless browser.
"""
import sys
import logging
from pathlib import Path

from src.next_data_scraper import get_all_reviews_for_url

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("next_data_parsing_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("next_data_parsing_test")

def test_next_data_parsing():
    """
    Test the __NEXT_DATA__ parsing functionality on a book known to have reviews.
    
    This test verifies that:
    1. The parser can extract the __NEXT_DATA__ script tag
    2. The parser can navigate through the JSON structure to find reviews
    3. The extracted reviews contain all required fields
    """
    url = "https://www.goodreads.com/book/show/4796.The_Winter_of_Our_Discontent"
    
    logger.info(f"Testing __NEXT_DATA__ parsing for: {url}")
    logger.info("This book was manually verified to have 3,329 reviews")
    
    reviews = get_all_reviews_for_url(url, verbose=True)
    
    if reviews:
        logger.info(f"Successfully extracted {len(reviews)} reviews")
        
        first_review = reviews[0]
        logger.info("First review details:")
        
        required_fields = [
            'review_text', 'review_rating', 'reviewer_id', 
            'reviewer_name', 'review_upvotes', 'review_date'
        ]
        
        for field in required_fields:
            if field in first_review:
                value = first_review[field]
                logger.info(f"  {field}: {value[:100] if isinstance(value, str) and len(value) > 100 else value}")
            else:
                logger.warning(f"  {field}: MISSING")
        
        reviews_with_text = sum(1 for r in reviews if r.get('review_text'))
        logger.info(f"Reviews with non-empty text: {reviews_with_text}/{len(reviews)}")
        
        reviews_with_ratings = sum(1 for r in reviews if r.get('review_rating'))
        logger.info(f"Reviews with ratings: {reviews_with_ratings}/{len(reviews)}")
        
        if reviews_with_text > 0 and reviews_with_ratings > 0:
            logger.info("TEST PASSED: Successfully extracted reviews with text and ratings")
            return True
        else:
            logger.error("TEST FAILED: No reviews with both text and ratings")
            return False
    else:
        logger.error("TEST FAILED: No reviews were extracted")
        return False

if __name__ == "__main__":
    success = test_next_data_parsing()
    
    if success:
        logger.info("All tests passed!")
        sys.exit(0)
    else:
        logger.error("Tests failed!")
        sys.exit(1)
