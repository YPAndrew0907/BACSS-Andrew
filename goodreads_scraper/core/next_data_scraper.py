"""
Goodreads review scraper that extracts data from the __NEXT_DATA__ script tag.

This approach avoids the need for a headless browser by parsing the JSON data
that's already embedded in the page's HTML within a script tag.
"""
import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import re

import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('next_data_scraper')


class GoodreadsNextDataScraper:
    """
    Scraper that extracts review data from the __NEXT_DATA__ script tag in Goodreads pages.
    
    This scraper works by:
    1. Fetching the Goodreads book page HTML
    2. Extracting the __NEXT_DATA__ script tag which contains JSON data
    3. Parsing the JSON to find review data
    4. Extracting review text, ratings, reviewer info, etc.
    
    The scraper includes:
    - Rate limiting to respect robots.txt
    - Caching to reduce redundant requests
    - Retry logic for handling network errors
    - Verbose logging for debugging
    """

    def __init__(self, cache_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the scraper.

        Args:
            cache_dir: Directory to cache responses. If None, no caching is performed.
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Caching enabled. Cache directory: {self.cache_dir}")

    def _rate_limit(self):
        """
        Implement rate limiting to respect robots.txt.
        
        Sleeps for 2 seconds between requests to avoid overloading the server.
        """
        time.sleep(2)  # Sleep for 2 seconds between requests

    def _get_cache_path(self, url: str, params: Optional[Dict] = None) -> Path:
        """
        Get the cache path for a URL.

        Args:
            url: URL to cache
            params: Query parameters

        Returns:
            Path to the cache file
        """
        if not self.cache_dir:
            raise ValueError("Cache directory not set")
        
        param_str = ""
        if params:
            param_str = "_" + "_".join(f"{k}={v}" for k, v in sorted(params.items()))
        
        clean_url = url.replace("https://", "").replace("http://", "")
        clean_url = re.sub(r'[\\/*?:"<>|]', "_", clean_url)
        
        return self.cache_dir / f"{clean_url}{param_str}.html"

    def _cache_response(self, url: str, response: requests.Response, params: Optional[Dict] = None):
        """
        Cache a response.

        Args:
            url: URL that was requested
            response: Response to cache
            params: Query parameters
        """
        if not self.cache_dir:
            return
        
        cache_path = self._get_cache_path(url, params)
        
        with open(cache_path, 'wb') as f:
            f.write(response.content)
            
        logger.debug(f"Cached response to {cache_path}")

    def _get_cached_response(self, url: str, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """
        Get a cached response.

        Args:
            url: URL to get cached response for
            params: Query parameters

        Returns:
            Cached response or None if not cached
        """
        if not self.cache_dir:
            return None
        
        cache_path = self._get_cache_path(url, params)
        
        if not cache_path.exists():
            return None
        
        response = requests.Response()
        response.status_code = 200
        
        with open(cache_path, 'rb') as f:
            response._content = f.read()
        
        logger.debug(f"Using cached response from {cache_path}")
        return response

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, ConnectionError))
    )
    def _make_request(self, url: str, params: Optional[Dict] = None) -> requests.Response:
        """
        Make a request with retries and caching.

        Args:
            url: URL to request
            params: Query parameters

        Returns:
            Response object
        """
        cached_response = self._get_cached_response(url, params)
        if cached_response:
            logger.debug(f"Using cached response for {url}")
            return cached_response
        
        self._rate_limit()
        
        logger.debug(f"Making request to {url}")
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code != 200:
            logger.warning(f"Request failed with status {response.status_code}: {url}")
            if response.status_code == 429:
                logger.warning("Rate limited. Waiting longer before retry...")
                time.sleep(10)  # Wait longer for rate limiting
        
        if response.status_code == 200:
            self._cache_response(url, response, params)
        
        return response

    def extract_next_data(self, html: str, verbose: bool = False) -> Optional[Dict]:
        """
        Extract the __NEXT_DATA__ JSON from HTML.

        Args:
            html: HTML content
            verbose: Whether to print verbose output

        Returns:
            Parsed JSON data or None if not found
        """
        soup = BeautifulSoup(html, 'html.parser')
        next_data_script = soup.select_one('script#__NEXT_DATA__')
        
        if not next_data_script:
            if verbose:
                logger.warning("No __NEXT_DATA__ script found in HTML")
            return None
        
        try:
            json_data = json.loads(next_data_script.string)
            if verbose:
                logger.info("Successfully extracted __NEXT_DATA__ JSON")
            return json_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse __NEXT_DATA__ JSON: {e}")
            return None

    def extract_reviews_from_next_data(self, next_data: Dict, verbose: bool = False) -> List[Dict]:
        """
        Extract reviews from __NEXT_DATA__ JSON.

        Args:
            next_data: Parsed __NEXT_DATA__ JSON
            verbose: Whether to print verbose output

        Returns:
            List of review dictionaries
        """
        reviews = []
        
        try:
            # Navigate through the JSON structure to find reviews
            props = next_data.get('props', {})
            page_props = props.get('pageProps', {})
            apollo_state = page_props.get('apolloState', {})
            
            if verbose:
                logger.info("Searching for review references in apolloState")
                
                # Log the keys in apolloState to help with debugging
                apollo_keys = list(apollo_state.keys())
                review_keys = [k for k in apollo_keys if k.startswith('Review:')]
                if review_keys:
                    logger.info(f"Found {len(review_keys)} Review keys in apolloState")
                    logger.info(f"Sample Review key: {review_keys[0]}")
            
            review_refs = []
            root_query = apollo_state.get('ROOT_QUERY', {})
            
            book_keys = [k for k in root_query.keys() if 'book(' in k]
            
            if book_keys and verbose:
                logger.info(f"Found {len(book_keys)} book entries in ROOT_QUERY")
            
            for book_key in book_keys:
                book = root_query.get(book_key, {})
                if 'reviews' in book:
                    edges = book.get('reviews', {}).get('edges', [])
                    
                    if edges and verbose:
                        logger.info(f"Found {len(edges)} review edges in book {book_key}")
                    
                    for edge in edges:
                        if isinstance(edge, dict) and 'node' in edge:
                            node = edge.get('node', {})
                            if isinstance(node, dict) and '__ref' in node:
                                review_refs.append(node.get('__ref'))
            
            if not review_refs:
                review_keys = [k for k in apollo_state.keys() if k.startswith('Review:')]
                if review_keys and verbose:
                    logger.info(f"Found {len(review_keys)} Review objects directly in apolloState")
                review_refs = review_keys
            
            if not review_refs:
                if verbose:
                    logger.info("No review references found, trying alternative paths")
                
                initial_state = page_props.get('initialState', {})
                books = initial_state.get('books', {})
                current_book = books.get('current', {})
                reviews_data = current_book.get('reviews', [])
                
                if reviews_data and verbose:
                    logger.info(f"Found {len(reviews_data)} reviews in initialState.books.current.reviews")
                
                for review in reviews_data:
                    if not isinstance(review, dict):
                        continue
                    
                    review_dict = {
                        'review_text': review.get('text', review.get('body', '')),
                        'review_rating': review.get('rating', None),
                        'reviewer_id': review.get('user', {}).get('id', review.get('userId', '')),
                        'reviewer_name': review.get('user', {}).get('name', review.get('userName', '')),
                        'review_upvotes': review.get('likesCount', review.get('likes', 0)),
                        'review_date': review.get('createdAt', review.get('dateAdded', '')),
                        'review_url': review.get('url', ''),
                    }
                    
                    # For debugging
                    if verbose:
                        logger.info(f"Review dict before validation: {review_dict}")
                    
                    if (review_dict.get('review_text') or review_dict.get('review_rating')):
                        if not review_dict.get('reviewer_id'):
                            review_dict['reviewer_id'] = f"unknown_{len(reviews)}"
                        
                        reviews.append(review_dict)
                        if verbose:
                            logger.info(f"Added review with text length: {len(str(review_dict.get('review_text', '')))}")
                            logger.info(f"Added review with rating: {review_dict.get('review_rating')}")
                
                if not reviews:
                    initial_data = page_props.get('initialData', {})
                    book_data = initial_data.get('book', {})
                    reviews_data = book_data.get('reviews', [])
                    
                    if reviews_data and verbose:
                        logger.info(f"Found {len(reviews_data)} reviews in initialData.book.reviews")
                    
                    for review in reviews_data:
                        if not isinstance(review, dict):
                            continue
                        
                        review_dict = {
                            'review_text': review.get('text', review.get('body', '')),
                            'review_rating': review.get('rating', None),
                            'reviewer_id': review.get('user', {}).get('id', review.get('userId', '')),
                            'reviewer_name': review.get('user', {}).get('name', review.get('userName', '')),
                            'review_upvotes': review.get('likesCount', review.get('likes', 0)),
                            'review_date': review.get('createdAt', review.get('dateAdded', '')),
                            'review_url': review.get('url', ''),
                        }
                        
                        if review_dict['review_text'] and review_dict['reviewer_id']:
                            reviews.append(review_dict)
            
            if review_refs and not reviews:
                if verbose:
                    logger.info(f"Processing {len(review_refs)} review references")
                
                # Extract review data from each reference
                for ref in review_refs:
                    review_obj = apollo_state.get(ref)
                    
                    if not review_obj:
                        if verbose:
                            logger.warning(f"Could not find review data for reference: {ref}")
                        continue
                    
                    if verbose and review_obj:
                        logger.info(f"Found review object for reference: {ref}")
                        logger.info(f"Review object keys: {list(review_obj.keys())}")
                    
                    # Extract review data
                    review_dict = {}
                    
                    # Extract review text - it's directly in the 'text' field as HTML
                    review_text = review_obj.get('text', review_obj.get('body', ''))
                    if isinstance(review_text, dict) and '__ref' in review_text:
                        text_ref = review_text.get('__ref')
                        text_obj = apollo_state.get(text_ref, {})
                        review_text = text_obj.get('text', text_obj.get('body', ''))
                    
                    if review_text and isinstance(review_text, str):
                        import re
                        review_text = re.sub(r'<br\s*/?>', '\n', review_text)  # Convert <br> to newlines
                        review_text = re.sub(r'<[^>]+>', '', review_text)  # Remove other HTML tags
                    
                    review_dict['review_text'] = review_text
                    
                    review_dict['review_rating'] = review_obj.get('rating')
                    
                    # Extract reviewer info
                    user_ref = review_obj.get('creator', review_obj.get('user', {}))
                    if isinstance(user_ref, dict) and '__ref' in user_ref:
                        user_ref_id = user_ref.get('__ref')
                        if verbose:
                            logger.info(f"Found user reference: {user_ref_id}")
                        
                        user_obj = apollo_state.get(user_ref_id, {})
                        if user_obj:
                            review_dict['reviewer_id'] = user_obj.get('legacyId', user_obj.get('id', ''))
                            review_dict['reviewer_name'] = user_obj.get('name', '')
                            
                            if verbose:
                                logger.info(f"Extracted reviewer ID: {review_dict['reviewer_id']}")
                                logger.info(f"Extracted reviewer name: {review_dict['reviewer_name']}")
                    else:
                        review_dict['reviewer_id'] = review_obj.get('userId', review_obj.get('id', ''))
                        review_dict['reviewer_name'] = review_obj.get('userName', '')
                    
                    review_dict['review_upvotes'] = review_obj.get('likesCount', review_obj.get('likes', 0))
                    review_dict['review_date'] = review_obj.get('createdAt', review_obj.get('dateAdded', ''))
                    review_dict['review_url'] = review_obj.get('url', '')
                    
                    # For debugging
                    if verbose:
                        logger.info(f"Review dict before validation: {review_dict}")
                    
                    if (review_dict.get('review_text') or review_dict.get('review_rating')):
                        if not review_dict.get('reviewer_id'):
                            review_dict['reviewer_id'] = f"unknown_{len(reviews)}"
                        
                        reviews.append(review_dict)
                        if verbose:
                            logger.info(f"Added review with text length: {len(str(review_dict.get('review_text', '')))}")
                            logger.info(f"Added review with rating: {review_dict.get('review_rating')}")
            
            if not reviews:
                dehydrated = page_props.get('dehydratedState', {})
                queries = dehydrated.get('queries', [])
                
                for query in queries:
                    state = query.get('state', {})
                    data = state.get('data', {})
                    
                    if 'book' in data:
                        book_data = data.get('book', {})
                        edges = book_data.get('reviews', {}).get('edges', [])
                        
                        if edges and verbose:
                            logger.info(f"Found {len(edges)} review edges in dehydratedState")
                        
                        for edge in edges:
                            node = edge.get('node', {})
                            if not isinstance(node, dict):
                                continue
                            
                            review_dict = {
                                'review_text': node.get('text', node.get('body', '')),
                                'review_rating': node.get('rating', None),
                                'reviewer_id': node.get('user', {}).get('id', node.get('userId', '')),
                                'reviewer_name': node.get('user', {}).get('name', node.get('userName', '')),
                                'review_upvotes': node.get('likesCount', node.get('likes', 0)),
                                'review_date': node.get('createdAt', node.get('dateAdded', '')),
                                'review_url': node.get('url', ''),
                            }
                            
                            if review_dict['review_text'] and review_dict['reviewer_id']:
                                reviews.append(review_dict)
            
            if not reviews and verbose:
                logger.info("No reviews found in __NEXT_DATA__, checking for reviews in raw HTML")
                
                
            if verbose:
                if reviews:
                    logger.info(f"Successfully extracted {len(reviews)} valid reviews")
                else:
                    logger.warning("Could not find any reviews in __NEXT_DATA__")
                    
                    # Dump the structure for debugging
                    with open('next_data_structure.json', 'w') as f:
                        json.dump(next_data, f, indent=2)
                    logger.info("Dumped __NEXT_DATA__ structure to next_data_structure.json for debugging")
            
        except Exception as e:
            logger.error(f"Error extracting reviews from __NEXT_DATA__: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return reviews

    def get_reviews_from_page(self, book_url: str, page: int = 1, verbose: bool = False) -> List[Dict]:
        """
        Get reviews from a specific page using __NEXT_DATA__ extraction.

        Args:
            book_url: URL of the book page
            page: Page number
            verbose: Whether to print verbose output

        Returns:
            List of review dictionaries
        """
        reviews_url = f"{book_url.rstrip('/')}/reviews"
        params = {"page": page}
        
        try:
            response = self._make_request(reviews_url, params=params)
            
            status_code = response.status_code
            if verbose:
                logger.info(f"HTTP Status Code: {status_code}")
                
            if status_code != 200:
                logger.warning(f"Failed to get reviews from page {page}: {status_code}")
                return []
            
            html_length = len(response.text)
            if verbose:
                logger.info(f"Raw HTML Length: {html_length} characters")
            
            next_data = self.extract_next_data(response.text, verbose)
            
            if not next_data:
                if verbose:
                    logger.warning("No __NEXT_DATA__ found in the page")
                return []
            
            reviews = self.extract_reviews_from_next_data(next_data, verbose)
            
            if verbose:
                logger.info(f"Extracted {len(reviews)} reviews from __NEXT_DATA__")
                
                if len(reviews) == 0:
                    debug_path = Path(f"debug_next_data_page_{page}.json")
                    with open(debug_path, 'w', encoding='utf-8') as f:
                        json.dump(next_data, f, indent=2)
                    logger.info(f"Saved __NEXT_DATA__ to {debug_path} for inspection")
            
            return reviews
            
        except Exception as e:
            logger.error(f"Error getting reviews from page {page}: {e}")
            return []

    def get_review_pages_count(self, book_url: str) -> int:
        """
        Get the number of review pages for a book.

        Args:
            book_url: URL of the book page

        Returns:
            Number of review pages
        """
        reviews_url = f"{book_url.rstrip('/')}/reviews"
        
        try:
            response = self._make_request(reviews_url)
            
            if response.status_code != 200:
                logger.warning(f"Failed to get review pages count: {response.status_code}")
                return 1
            
            next_data = self.extract_next_data(response.text)
            
            if not next_data:
                logger.warning("No __NEXT_DATA__ found in the page")
                return 1
            
            try:
                props = next_data.get('props', {})
                page_props = props.get('pageProps', {})
                
                pagination = None
                
                apollo_state = page_props.get('apolloState', {})
                root_query = apollo_state.get('ROOT_QUERY', {})
                
                book_keys = [k for k in root_query.keys() if 'book(' in k]
                
                if book_keys:
                    for book_key in book_keys:
                        book = root_query.get(book_key, {})
                        if 'reviews' in book:
                            pagination = book.get('reviews', {}).get('pageInfo', {})
                
                if not pagination:
                    initial_state = page_props.get('initialState', {})
                    books = initial_state.get('books', {})
                    current_book = books.get('current', {})
                    review_stats = current_book.get('reviewStats', {})
                    
                    if review_stats:
                        total_reviews = review_stats.get('totalReviews', 0)
                        per_page = 30  # Default per page
                        return (total_reviews + per_page - 1) // per_page
                
                if not pagination:
                    dehydrated = page_props.get('dehydratedState', {})
                    queries = dehydrated.get('queries', [])
                    
                    for query in queries:
                        state = query.get('state', {})
                        data = state.get('data', {})
                        
                        if 'book' in data:
                            book_data = data.get('book', {})
                            reviews = book_data.get('reviews', {})
                            pagination = reviews.get('pageInfo', {})
                
                if pagination:
                    total_pages = pagination.get('totalPages', 1)
                    return total_pages
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                pagination_elements = soup.select('.pagination')
                
                if pagination_elements:
                    pagination = pagination_elements[0]
                    page_links = pagination.select('a')
                    
                    if page_links:
                        page_numbers = []
                        for link in page_links:
                            try:
                                page_num = int(link.text.strip())
                                page_numbers.append(page_num)
                            except ValueError:
                                continue
                        
                        if page_numbers:
                            return max(page_numbers)
                
                return 1
                
            except Exception as e:
                logger.error(f"Error parsing pagination info: {e}")
                return 1
            
        except Exception as e:
            logger.error(f"Error getting review pages count: {e}")
            return 1

    def get_all_reviews(self, book_url: str, max_pages: Optional[int] = None) -> List[Dict]:
        """
        Get all reviews for a book.

        Args:
            book_url: URL of the book page
            max_pages: Maximum number of pages to scrape (None for all)

        Returns:
            List of review dictionaries
        """
        total_pages = self.get_review_pages_count(book_url)

        if max_pages is not None:
            total_pages = min(total_pages, max_pages)

        logger.info(f"Found {total_pages} review pages for {book_url}")

        all_reviews = []

        for page in tqdm(range(1, total_pages + 1), desc="Scraping review pages"):
            reviews = self.get_reviews_from_page(book_url, page)
            all_reviews.extend(reviews)

            logger.info(f"Scraped {len(reviews)} reviews from page {page}")

        return all_reviews

    def scrape_book_reviews(self, book_data: Dict, max_pages: Optional[int] = None) -> Dict:
        """
        Scrape reviews for a book.

        Args:
            book_data: Dictionary with book data including goodreads_url
            max_pages: Maximum number of pages to scrape (optional)

        Returns:
            Dictionary with book data and reviews
        """
        book_url = book_data.get('goodreads_url')
        if pd.isna(book_url) or not book_url:
            logger.warning(f"No Goodreads URL for book: {book_data.get('title', 'Unknown')}")
            return {**book_data, 'reviews': []}

        logger.info(f"Scraping reviews for book: {book_data.get('title', 'Unknown')}")

        reviews = self.get_all_reviews(book_url, max_pages=max_pages)
        
        if not reviews:
            logger.warning(f"No reviews found for {book_data.get('title', 'Unknown')}")

        logger.info(f"Scraped {len(reviews)} reviews for book: {book_data.get('title', 'Unknown')}")

        return {**book_data, 'reviews': reviews}

    def process_book_list(self, books_df: Union[pd.DataFrame, str, Path], max_pages: Optional[int] = None) -> pd.DataFrame:
        """
        Process a list of books and scrape reviews.

        Args:
            books_df: DataFrame with book data including goodreads_url, or path to CSV file
            max_pages: Maximum number of pages to scrape per book (optional)

        Returns:
            DataFrame with reviews data
        """
        if isinstance(books_df, (str, Path)):
            logger.info(f"Loading book list from file: {books_df}")
            books_df = pd.read_csv(books_df)
            
        if 'goodreads_url' not in books_df.columns:
            raise ValueError("DataFrame must contain 'goodreads_url' column")

        all_reviews = []

        for idx, row in tqdm(books_df.iterrows(), total=len(books_df), desc="Scraping books"):
            book_data = row.to_dict()

            try:
                book_with_reviews = self.scrape_book_reviews(book_data, max_pages=max_pages)

                for review in book_with_reviews['reviews']:
                    review_row = {
                        'book_id': book_data.get('book_id'),
                        'title': book_data.get('title'),
                        'author': book_data.get('author'),
                        'goodreads_url': book_data.get('goodreads_url'),
                        **review
                    }
                    all_reviews.append(review_row)

            except Exception as e:
                logger.error(f"Error processing book {book_data.get('title', 'Unknown')}: {e}")

        if all_reviews:
            reviews_df = pd.DataFrame(all_reviews)

            for col in ['book_id', 'review_text', 'review_rating']:
                if col in reviews_df.columns:
                    null_count = reviews_df[col].isna().sum()
                    if null_count > 0:
                        logger.warning(f"Found {null_count} null values in '{col}' column")

            if 'review_rating' in reviews_df.columns:
                reviews_df['review_rating'] = reviews_df['review_rating'].apply(
                    lambda x: int(x) if pd.notna(x) and 1 <= x <= 5 else None
                )

            return reviews_df
        else:
            return pd.DataFrame()


def get_all_reviews_for_url(url: str, verbose: bool = False) -> List[Dict]:
    """
    Get all reviews for a specific book URL.
    
    Args:
        url: Goodreads book URL
        verbose: Whether to print verbose diagnostic information
        
    Returns:
        List of review dictionaries
    """
    scraper = GoodreadsNextDataScraper(cache_dir=Path("data/cache"))
    
    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.info(f"Testing review scraping for URL: {url}")
    
    total_pages = scraper.get_review_pages_count(url)
    logger.info(f"Found {total_pages} review pages for {url}")
    
    all_reviews = []
    
    for page in range(1, total_pages + 1):
        logger.info(f"Scraping page {page}/{total_pages}")
        reviews = scraper.get_reviews_from_page(url, page, verbose=verbose)
        all_reviews.extend(reviews)
        
        logger.info(f"Scraped {len(reviews)} reviews from page {page}")
        
        if len(reviews) == 0 and verbose:
            logger.warning(f"No reviews found on page {page}, but continuing to next page")
    
    logger.info(f"Total reviews scraped: {len(all_reviews)}")
    return all_reviews


def main():
    """Main function to run the review scraper script."""
    parser = argparse.ArgumentParser(description="Goodreads Review Scraper (NEXT_DATA)")
    parser.add_argument("--sample", action="store_true", help="Use sample data")
    parser.add_argument("--single-book", type=str, help="URL of a single book to scrape")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--max-pages", type=int, help="Maximum number of pages to scrape")
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.info("Verbose mode enabled")
    
    if args.single_book:
        logger.info(f"Single book mode: {args.single_book}")
        reviews = get_all_reviews_for_url(args.single_book, verbose=args.verbose)
        
        if reviews:
            logger.info(f"Successfully scraped {len(reviews)} reviews")
            
            output_path = Path("single_book_reviews.csv")
            reviews_df = pd.DataFrame(reviews)
            reviews_df.to_csv(output_path, index=False)
            logger.info(f"Reviews saved to {output_path}")
        else:
            logger.warning("No reviews were scraped")
        
        return
    
    if args.sample:
        input_path = Path("data/output/sample/goodreads_urls_sample.csv")
        output_path = Path("data/output/sample/reviews_output_sample.csv")
    else:
        input_path = Path("data/output/goodreads_urls.csv")
        output_path = Path("data/output/reviews_output.csv")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting review scraping process for {input_path}")

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        logger.info("Running book lookup first...")

        from book_lookup import main as book_lookup_main
        book_lookup_main(sample=args.sample)

        if not input_path.exists():
            logger.error(f"Failed to create input file: {input_path}")
            return

    books_df = pd.read_csv(input_path)

    scraper = GoodreadsNextDataScraper(cache_dir=Path("data/cache"))

    reviews_df = scraper.process_book_list(books_df)

    if not reviews_df.empty:
        reviews_df.to_csv(output_path, index=False)
        logger.info(f"Review scraping complete. Results saved to {output_path}")

        total_books = len(books_df)
        total_reviews = len(reviews_df)
        books_with_reviews = reviews_df['book_id'].nunique()

        logger.info(f"Summary: Scraped {total_reviews} reviews for {books_with_reviews}/{total_books} books")
        if books_with_reviews > 0:
            logger.info(f"Average reviews per book: {total_reviews/books_with_reviews:.1f}")
    else:
        logger.warning("No reviews were scraped")


if __name__ == "__main__":
    main()
