"""
Script to run the analyze_output.py script on the test output file.
"""
import sys
from pathlib import Path
from analyze_output import analyze_output

def main():
    """Run the analyze_output.py script on the test output file."""
    test_output_file = 'data/output/test/reviews_output_test.csv'
    analyze_output(test_output_file)

if __name__ == "__main__":
    main()
