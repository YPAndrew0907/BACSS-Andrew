"""
Script to create the demo.ipynb notebook programmatically using nbformat.
"""

import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = [
    nbf.v4.new_markdown_cell("""

This notebook demonstrates the functionality of the Goodreads review scraper. It uses the implemented `book_lookup.py` and `review_scraper.py` scripts to process the input CSV and produce the output CSV.

The scraper performs the following steps:
1. Reads the input CSV file with book_id, title, and author columns
2. Searches Goodreads for each book and finds the matching book page URL
3. Scrapes all reviews for each book
4. Aggregates the data into a single CSV file

The scraper implements the following features:
- Fuzzy string matching with RapidFuzz (threshold of 85)
- Rate limiting and robots.txt compliance
- Error handling and retries
- Response caching
- Pagination handling
"""),

    nbf.v4.new_markdown_cell("""

First, let's import the necessary modules and set up the environment.
"""),

    nbf.v4.new_code_cell("""
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm.notebook import tqdm

sys.path.append('../src')

from book_lookup import GoodreadsBookLookup
from review_scraper import GoodreadsReviewScraper

INPUT_PATH = Path('../data/input/goodreads_list.csv')
URLS_PATH = Path('../data/output/goodreads_urls.csv')
OUTPUT_PATH = Path('../data/output/reviews_output.csv')
CACHE_DIR = Path('../data/cache')

CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
"""),

    nbf.v4.new_markdown_cell("""

Let's load the input CSV file and explore its contents.
"""),

    nbf.v4.new_code_cell("""
input_df = pd.read_csv(INPUT_PATH)

print(f"Input data shape: {input_df.shape}")
input_df.head()
"""),

    nbf.v4.new_code_cell("""
print("Missing values:")
input_df.isna().sum()
"""),

    nbf.v4.new_markdown_cell("""

Now, let's use the `GoodreadsBookLookup` class to find the Goodreads URL for each book in the input CSV file.
"""),

    nbf.v4.new_code_cell("""
lookup = GoodreadsBookLookup(cache_dir=CACHE_DIR)

demo_books = input_df.head(5).copy()

for idx, row in tqdm(demo_books.iterrows(), total=len(demo_books), desc="Looking up books"):
    book_id = row['book_id']
    title = row['title']
    author = row['author']
    
    print(f"\\nProcessing book: '{title}' by '{author}'")
    
    search_results = lookup.search_book(title, author)
    print(f"Found {len(search_results)} search results")
    
    best_match = lookup.find_best_match(title, author, search_results)
    
    if best_match:
        print(f"Best match: '{best_match['title']}' by '{best_match['author']}'")
        print(f"URL: {best_match['url']}")
        demo_books.at[idx, 'goodreads_url'] = best_match['url']
    else:
        print(f"No good match found for '{title}' by '{author}'")
        demo_books.at[idx, 'goodreads_url'] = None
"""),

    nbf.v4.new_code_cell("""
demo_books
"""),

    nbf.v4.new_markdown_cell("""

Now, let's process all books in the input CSV file. This may take a while, so we'll use the `process_book_list` method from the `GoodreadsBookLookup` class.
"""),

    nbf.v4.new_code_cell("""
if URLS_PATH.exists():
    print(f"Loading existing URLs from {URLS_PATH}")
    books_with_urls = pd.read_csv(URLS_PATH)
else:
    print(f"Processing all books to find Goodreads URLs")
    books_with_urls = lookup.process_book_list(INPUT_PATH)
    
    books_with_urls.to_csv(URLS_PATH, index=False)
    print(f"Saved URLs to {URLS_PATH}")

total_books = len(books_with_urls)
found_urls = books_with_urls['goodreads_url'].notna().sum()
print(f"Found URLs for {found_urls}/{total_books} books ({found_urls/total_books:.1%})")
"""),

    nbf.v4.new_markdown_cell("""

Now, let's use the `GoodreadsReviewScraper` class to scrape reviews for each book.
"""),

    nbf.v4.new_code_cell("""
scraper = GoodreadsReviewScraper(cache_dir=CACHE_DIR)

demo_book = books_with_urls[books_with_urls['goodreads_url'].notna()].iloc[0]
print(f"Scraping reviews for: '{demo_book['title']}' by '{demo_book['author']}'")

total_pages = scraper.get_review_pages_count(demo_book['goodreads_url'])
print(f"Found {total_pages} review pages")

reviews = scraper.get_reviews_from_page(demo_book['goodreads_url'], page=1)
print(f"Scraped {len(reviews)} reviews from page 1")

if reviews:
    review = reviews[0]
    print("\\nSample review:")
    print(f"Text: {review['review_text'][:200]}...")
    print(f"Rating: {review['review_rating']}")
    print(f"Reviewer: {review['reviewer_name']} (ID: {review['reviewer_id']})")
    print(f"Upvotes: {review['review_upvotes']}")
    print(f"Date: {review['review_date']}")
    print(f"Shelves: {review['shelves']}")
    print(f"Comment count: {review['comment_count']}")
"""),

    nbf.v4.new_markdown_cell("""

Now, let's process all books to scrape reviews. This will take a long time, so we'll use the `process_book_list` method from the `GoodreadsReviewScraper` class.
"""),

    nbf.v4.new_code_cell("""
if OUTPUT_PATH.exists():
    print(f"Loading existing reviews from {OUTPUT_PATH}")
    reviews_df = pd.read_csv(OUTPUT_PATH)
else:
    print(f"Processing all books to scrape reviews")
    demo_books_with_urls = books_with_urls[books_with_urls['goodreads_url'].notna()].head(3)
    
    reviews_df = scraper.process_book_list(demo_books_with_urls)
    
    reviews_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved reviews to {OUTPUT_PATH}")

if not reviews_df.empty:
    total_reviews = len(reviews_df)
    books_with_reviews = reviews_df['book_id'].nunique()
    print(f"Scraped {total_reviews} reviews for {books_with_reviews} books")
    print(f"Average reviews per book: {total_reviews/books_with_reviews:.1f}")
else:
    print("No reviews were scraped")
"""),

    nbf.v4.new_markdown_cell("""

Let's analyze the scraped reviews data.
"""),

    nbf.v4.new_code_cell("""
if not reviews_df.empty:
    print(f"Reviews data shape: {reviews_df.shape}")
    reviews_df.head()
"""),

    nbf.v4.new_code_cell("""
if not reviews_df.empty:
    print("Missing values:")
    reviews_df.isna().sum()
"""),

    nbf.v4.new_code_cell("""
if not reviews_df.empty and 'review_rating' in reviews_df.columns:
    plt.figure(figsize=(10, 6))
    reviews_df['review_rating'].value_counts().sort_index().plot(kind='bar')
    plt.title('Distribution of Ratings')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.show()
"""),

    nbf.v4.new_code_cell("""
if not reviews_df.empty and 'review_rating' in reviews_df.columns:
    avg_ratings = reviews_df.groupby(['book_id', 'title'])['review_rating'].mean().reset_index()
    avg_ratings = avg_ratings.sort_values('review_rating', ascending=False)
    
    plt.figure(figsize=(12, 6))
    plt.barh(avg_ratings['title'], avg_ratings['review_rating'])
    plt.title('Average Rating per Book')
    plt.xlabel('Average Rating')
    plt.ylabel('Book Title')
    plt.xlim(0, 5)
    plt.tight_layout()
    plt.show()
"""),

    nbf.v4.new_code_cell("""
if not reviews_df.empty:
    review_counts = reviews_df.groupby(['book_id', 'title']).size().reset_index(name='review_count')
    review_counts = review_counts.sort_values('review_count', ascending=False)
    
    plt.figure(figsize=(12, 6))
    plt.barh(review_counts['title'], review_counts['review_count'])
    plt.title('Number of Reviews per Book')
    plt.xlabel('Number of Reviews')
    plt.ylabel('Book Title')
    plt.tight_layout()
    plt.show()
"""),

    nbf.v4.new_markdown_cell("""

Let's perform some data quality checks on the scraped reviews data.
"""),

    nbf.v4.new_code_cell("""
if not reviews_df.empty:
    required_columns = ['book_id', 'review_text', 'review_rating']
    for col in required_columns:
        if col in reviews_df.columns:
            null_count = reviews_df[col].isna().sum()
            print(f"Nulls in '{col}': {null_count} ({null_count/len(reviews_df):.1%})")
        else:
            print(f"Column '{col}' not found in the data")
"""),

    nbf.v4.new_code_cell("""
if not reviews_df.empty and 'review_rating' in reviews_df.columns:
    valid_ratings = reviews_df['review_rating'].apply(lambda x: pd.isna(x) or (isinstance(x, (int, float)) and 1 <= x <= 5))
    invalid_count = (~valid_ratings).sum()
    print(f"Invalid ratings: {invalid_count} ({invalid_count/len(reviews_df):.1%})")
"""),

    nbf.v4.new_code_cell("""
if not reviews_df.empty and 'review_date' in reviews_df.columns:
    import re
    iso_pattern = re.compile(r'^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}$')
    valid_dates = reviews_df['review_date'].apply(lambda x: pd.isna(x) or (isinstance(x, str) and iso_pattern.match(x)))
    invalid_count = (~valid_dates).sum()
    print(f"Invalid dates: {invalid_count} ({invalid_count/len(reviews_df):.1%})")
"""),

    nbf.v4.new_markdown_cell("""

Now, let's run the full pipeline to process all books and scrape all reviews. This will take a long time, so we'll use the main functions from the `book_lookup.py` and `review_scraper.py` scripts.
"""),

    nbf.v4.new_code_cell("""
def run_full_pipeline():
    print("Running full pipeline...")
    
    from book_lookup import main as book_lookup_main
    book_lookup_main()
    
    from review_scraper import main as review_scraper_main
    review_scraper_main()
    
    print("Full pipeline complete!")

"""),

    nbf.v4.new_markdown_cell("""

In this notebook, we demonstrated the functionality of the Goodreads review scraper. We showed how to:

1. Load and explore the input data
2. Look up books on Goodreads using fuzzy matching
3. Scrape reviews for each book
4. Analyze the scraped reviews data
5. Perform data quality checks
6. Run the full pipeline

The scraper implements all the required features:
- Fuzzy string matching with RapidFuzz (threshold of 85)
- Rate limiting and robots.txt compliance
- Error handling and retries
- Response caching
- Pagination handling

The output CSV file contains all the required fields:
- book_id, title, author (from the input CSV)
- review_text (full body)
- review_rating (1-5 stars)
- reviewer_id (user profile link or numeric ID)
- review_upvotes ("likes" on the review)
- review_downvotes (if exposed)
- review_date
- Additional metadata (shelves, comment count, etc.)
""")
]

nb['cells'] = cells

with open('demo.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Notebook created successfully!")
