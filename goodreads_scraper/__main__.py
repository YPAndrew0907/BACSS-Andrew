"""
Main entry point for the Goodreads Scraper package.
"""
import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from goodreads_scraper.runners.run_full_scraper import main as run_full_scraper
from goodreads_scraper.runners.run_sample import main as run_sample
from goodreads_scraper.utils.generate_report import main as generate_report


def main():
    """Main entry point for the Goodreads Scraper package."""
    parser = argparse.ArgumentParser(description="Goodreads Review Scraper")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    full_parser = subparsers.add_parser("full", help="Run the full scraper")
    
    sample_parser = subparsers.add_parser("sample", help="Run the scraper with sample data")
    
    report_parser = subparsers.add_parser("report", help="Generate a final report")
    
    args = parser.parse_args()
    
    if args.command == "full":
        run_full_scraper()
    elif args.command == "sample":
        run_sample()
    elif args.command == "report":
        generate_report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
