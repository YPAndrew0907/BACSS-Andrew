set -e


echo "Setting up virtual environment..."
python -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install requests beautifulsoup4 rapidfuzz pandas tqdm tenacity pytest ruff

echo "Running linting with ruff..."
ruff check src/ tests/ --exit-zero

echo "Running tests with pytest..."
pytest tests/ -v

echo "CI completed successfully!"
