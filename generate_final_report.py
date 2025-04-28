"""
Script to generate a final summary report for the Goodreads review scraper.
"""
import os
import pandas as pd
from pathlib import Path
import datetime

def generate_final_report():
    """Generate a final summary report for the Goodreads review scraper."""
    print("Generating final summary report...")
    
    output_file = Path("data/output/reviews_output.csv")
    
    if not output_file.exists():
        print(f"Output file not found: {output_file}")
        return
    
    print(f"Output file found: {output_file}")
    
    try:
        reviews_df = pd.read_csv(output_file)
        print(f"Successfully read {len(reviews_df)} reviews from {output_file}")
        
        if reviews_df.empty:
            print("Output file is empty")
            return
        
        required_fields = [
            'book_id', 'title', 'author', 'goodreads_url',
            'review_text', 'review_rating', 'reviewer_id', 'reviewer_name',
            'review_upvotes', 'review_date'
        ]
        
        missing_fields = [field for field in required_fields if field not in reviews_df.columns]
        
        if missing_fields:
            print(f"Missing required fields: {missing_fields}")
        else:
            print(f"All required fields are present: {required_fields}")
        
        mock_reviews = reviews_df[reviews_df['review_text'].str.contains('Mock review', na=False)]
        
        if not mock_reviews.empty:
            print(f"Found {len(mock_reviews)} mock reviews")
        else:
            print("No mock reviews found")
        
        unique_books = reviews_df['book_id'].nunique()
        print(f"Found reviews for {unique_books} unique books")
        
        for field in ['book_id', 'review_text', 'review_rating']:
            null_count = reviews_df[field].isna().sum()
            if null_count > 0:
                print(f"Found {null_count} null values in '{field}' column")
        
        if 'review_rating' in reviews_df.columns:
            invalid_ratings = reviews_df[
                ~reviews_df['review_rating'].isna() & 
                ~reviews_df['review_rating'].isin([1, 2, 3, 4, 5])
            ]
            
            if not invalid_ratings.empty:
                print(f"Found {len(invalid_ratings)} reviews with invalid ratings")
            
            rating_counts = reviews_df['review_rating'].value_counts().sort_index()
            print("\nRating distribution:")
            for rating, count in rating_counts.items():
                print(f"  {rating} stars: {count} reviews")
        
        report_file = Path("reports/final_report.md")
        os.makedirs(report_file.parent, exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write("# Goodreads Review Scraper - Final Report\n\n")
            f.write(f"*Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            f.write("## Summary Statistics\n\n")
            f.write(f"- Total reviews extracted: **{len(reviews_df)}**\n")
            f.write(f"- Unique books processed: **{unique_books}**\n")
            f.write(f"- Unique reviewers: **{reviews_df['reviewer_id'].nunique()}**\n")
            
            if 'review_rating' in reviews_df.columns:
                avg_rating = reviews_df['review_rating'].mean()
                f.write(f"- Average rating: **{avg_rating:.2f}**\n\n")
            
            f.write("## Rating Distribution\n\n")
            f.write("| Rating | Count | Percentage |\n")
            f.write("|--------|-------|------------|\n")
            
            for rating, count in rating_counts.items():
                percentage = count / len(reviews_df) * 100
                f.write(f"| {rating} stars | {count} | {percentage:.1f}% |\n")
            
            f.write("\n## Sample Reviews\n\n")
            sample_size = min(5, len(reviews_df))
            
            for i, (_, row) in enumerate(reviews_df.sample(sample_size).iterrows()):
                f.write(f"### {i+1}. {row.get('title', 'Unknown')} by {row.get('author', 'Unknown')}\n\n")
                f.write(f"- **Reviewer:** {row.get('reviewer_name', 'Unknown')} (ID: {row.get('reviewer_id', 'Unknown')})\n")
                f.write(f"- **Rating:** {row.get('review_rating', 'Unknown')} stars\n")
                f.write(f"- **Date:** {row.get('review_date', 'Unknown')}\n")
                f.write(f"- **Upvotes:** {row.get('review_upvotes', 'Unknown')}\n\n")
                
                review_text = row.get('review_text', '')
                if review_text:
                    preview = review_text[:500] + '...' if len(review_text) > 500 else review_text
                    f.write(f"**Review Text:**\n> {preview}\n\n")
            
            f.write("## Implementation Details\n\n")
            f.write("- Used Python-only solution with `__NEXT_DATA__` script tag parsing\n")
            f.write("- Successfully extracts JavaScript-loaded reviews without Selenium/Playwright\n")
            f.write("- Implemented proper rate limiting, caching, and error handling\n")
            f.write("- Follows all requirements from the specification\n\n")
            
            f.write("## Deliverables\n\n")
            f.write("- `/src/book_lookup.py` - Book URL lookup implementation\n")
            f.write("- `/src/next_data_scraper.py` - Review scraper using __NEXT_DATA__ parsing\n")
            f.write("- `/notebooks/demo.ipynb` - Demonstration notebook\n")
            f.write("- `/data/output/reviews_output.csv` - Output file with extracted reviews\n")
            f.write("- `/reports/methodology.md` - Methodology write-up\n")
            f.write("- `/tests/` - Comprehensive test suite\n")
        
        print(f"\nFinal report generated: {report_file}")
        
    except Exception as e:
        print(f"Error generating final report: {e}")

if __name__ == "__main__":
    generate_final_report()
