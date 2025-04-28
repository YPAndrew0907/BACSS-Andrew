"""
Setup script for the Goodreads Scraper package.
"""
from setuptools import setup, find_packages

setup(
    name="goodreads_scraper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "rapidfuzz",
        "pandas",
        "tqdm",
        "tenacity",
    ],
    entry_points={
        "console_scripts": [
            "goodreads-scraper=goodreads_scraper.__main__:main",
        ],
    },
    python_requires=">=3.6",
    description="A robust Python-based web scraper for extracting book reviews from Goodreads",
    author="Andrew Wang",
    author_email="mrmonkey666098@gmail.com",
)
