.PHONY: test test-unit test-integration test-all test-verbose clean lint format typecheck help

# Default target
help:
	@echo "Available targets:"
	@echo "  test             Run unit tests (excludes integration tests)"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-all         Run all tests including integration"
	@echo "  test-verbose     Run unit tests with verbose output"
	@echo "  lint             Run code linting with ruff"
	@echo "  format           Format code with black and ruff"
	@echo "  typecheck        Run mypy type checking"
	@echo "  clean            Remove Python cache files and test artifacts"

# Run unit tests (default, excludes integration)
test:
	python -m pytest tests/ -v -m "not integration"

# Alias for test
test-unit: test

# Run integration tests only
test-integration:
	python -m pytest tests/ -v -m integration

# Run all tests including integration
test-all:
	python -m pytest tests/ -v

# Run tests with extra verbose output and traceback
test-verbose:
	python -m pytest tests/ -vv -m "not integration" --tb=long

# Lint code
lint:
	ruff check src/ tests/

# Format code
format:
	black src/ tests/
	ruff check --fix src/ tests/

# Type check with mypy
typecheck:
	mypy src/ tests/

# Clean up cache and build artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete