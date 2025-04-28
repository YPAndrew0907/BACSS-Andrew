"""
Script to check cached review pages and verify extraction.
"""
import os
import json
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd

def check_cached_reviews():
    """Check cached review pages and verify extraction."""
    cache_dir = Path("data/cache")
    
    if not cache_dir.exists():
        print(f"Cache directory not found: {cache_dir}")
        return
    
    review_pages = list(cache_dir.glob("*reviews_page=1.html"))
    print(f"Found {len(review_pages)} cached review pages")
    
    if not review_pages:
        print("No cached review pages found")
        return
    
    sample_size = min(5, len(review_pages))
    print(f"\nExamining {sample_size} cached review pages:")
    
    for i, page_path in enumerate(review_pages[:sample_size]):
        print(f"\n{i+1}. {page_path.name}")
        
        try:
            with open(page_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            next_data = soup.select_one('script#__NEXT_DATA__')
            
            if next_data:
                print("  __NEXT_DATA__ script tag found")
                
                try:
                    data = json.loads(next_data.string)
                    
                    props = data.get('props', {})
                    page_props = props.get('pageProps', {})
                    apollo_state = page_props.get('apolloState', {})
                    
                    review_keys = [k for k in apollo_state.keys() if k.startswith('Review:')]
                    print(f"  Found {len(review_keys)} Review objects in apolloState")
                    
                    if review_keys:
                        first_review = apollo_state.get(review_keys[0], {})
                        print(f"  First review keys: {list(first_review.keys())}")
                        
                        review_text = first_review.get('text', '')
                        if isinstance(review_text, str):
                            preview = review_text[:100] + '...' if len(review_text) > 100 else review_text
                            print(f"  Review text: {preview}")
                        
                        rating = first_review.get('rating')
                        print(f"  Rating: {rating}")
                        
                        user_ref = first_review.get('user', {})
                        if isinstance(user_ref, dict) and '__ref' in user_ref:
                            user_ref_id = user_ref.get('__ref')
                            user_obj = apollo_state.get(user_ref_id, {})
                            print(f"  Reviewer: {user_obj.get('name')} (ID: {user_obj.get('id')})")
                    
                except json.JSONDecodeError as e:
                    print(f"  Error parsing JSON: {e}")
            else:
                print("  No __NEXT_DATA__ script tag found")
        
        except Exception as e:
            print(f"  Error examining page: {e}")
    
    print("\nVerification complete")

if __name__ == "__main__":
    check_cached_reviews()
