"""
Script to check for cached review pages with no reviews.
"""
from pathlib import Path
import re

def check_empty_reviews():
    """Check for cached review pages with no reviews."""
    cache_dir = Path("data/cache")
    
    if not cache_dir.exists():
        print(f"Cache directory not found: {cache_dir}")
        return
    
    review_pages = list(cache_dir.glob("*reviews_page=1.html"))
    print(f"Found {len(review_pages)} cached review pages")
    
    if not review_pages:
        print("No cached review pages found")
        return
    
    empty_pages = []
    sample_size = min(10, len(review_pages))
    
    print(f"\nChecking {sample_size} cached review pages for 'No reviews yet' message:")
    
    for i, page_path in enumerate(review_pages[:sample_size]):
        try:
            with open(page_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                if 'No reviews yet' in content:
                    empty_pages.append(page_path.name)
                    print(f"  {i+1}. {page_path.name} - No reviews found")
                else:
                    print(f"  {i+1}. {page_path.name} - Reviews found")
        
        except Exception as e:
            print(f"  Error reading {page_path.name}: {e}")
    
    print(f"\nFound {len(empty_pages)} pages with no reviews out of {sample_size} checked")

if __name__ == "__main__":
    check_empty_reviews()
