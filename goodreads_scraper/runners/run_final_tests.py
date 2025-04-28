"""
Script to run all tests to ensure all requirements are met.
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command):
    """Run a command and return the output."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    return result.returncode == 0

def run_tests():
    """Run all tests to ensure all requirements are met."""
    print("Running all tests to ensure all requirements are met...")
    
    print("\n=== Running pytest ===")
    success = run_command("python -m pytest tests/")
    
    if not success:
        print("Pytest failed!")
        return False
    
    print("\n=== Running ruff linting ===")
    success = run_command("ruff check src/ tests/")
    
    if not success:
        print("Ruff linting failed!")
        return False
    
    print("\n=== Running test_no_mock_reviews.py ===")
    success = run_command("python -m pytest tests/test_no_mock_reviews.py -v")
    
    if not success:
        print("test_no_mock_reviews.py failed!")
        return False
    
    print("\n=== Running test_next_data_scraper.py ===")
    success = run_command("python -m pytest tests/test_next_data_scraper.py -v")
    
    if not success:
        print("test_next_data_scraper.py failed!")
        return False
    
    print("\n=== Running CI script ===")
    success = run_command("bash run_ci.sh")
    
    if not success:
        print("CI script failed!")
        return False
    
    print("\nAll tests passed!")
    return True

def check_deliverables():
    """Check if all deliverables are ready."""
    print("\n=== Checking deliverables ===")
    
    deliverables = [
        "src/book_lookup.py",
        "src/next_data_scraper.py",
        "notebooks/demo.ipynb",
        "reports/methodology.md",
        "tests/test_matching.py",
        "tests/test_parse_review.py",
        "tests/test_end_to_end.py",
        "run_ci.sh"
    ]
    
    missing_deliverables = []
    
    for deliverable in deliverables:
        if not Path(deliverable).exists():
            missing_deliverables.append(deliverable)
    
    if missing_deliverables:
        print(f"Missing deliverables: {missing_deliverables}")
        return False
    
    print("All deliverables are ready!")
    return True

def main():
    """Run all tests and check deliverables."""
    print("=== Final Tests ===")
    
    tests_passed = run_tests()
    deliverables_ready = check_deliverables()
    
    if tests_passed and deliverables_ready:
        print("\n=== All requirements are met! ===")
        return 0
    else:
        print("\n=== Some requirements are not met! ===")
        return 1

if __name__ == "__main__":
    sys.exit(main())
