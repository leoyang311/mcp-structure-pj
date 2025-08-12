.PHONY: install dev-install test clean lint format run-cli run-api demo check-env docker-up docker-down

# Installation
install:
	uv sync

dev-install:
	uv sync --all-extras

# Testing
test:
	uv run pytest tests/ -v

# Code quality
lint:
	uv run ruff check .

format:
	uv run ruff format .

# Clean up
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf dist/
	rm -rf *.egg-info/

# Environment check
check-env:
	@echo "Checking environment variables..."
	@test -f .env || (echo "Error: .env file not found" && exit 1)
	@grep -q "OPENAI_API_KEY" .env || (echo "Error: OPENAI_API_KEY not found in .env" && exit 1)
	@grep -q "TAVILY_API_KEY" .env || (echo "Error: TAVILY_API_KEY not found in .env" && exit 1)
	@echo "Environment check passed ✓"

# Docker services
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Run applications
run-cli:
	uv run python start.py cli

run-api:
	uv run python start.py api

demo:
	uv run python demo_optimized.py

# Development setup
setup: check-env docker-up dev-install
	@echo "Development environment setup complete ✓"

# Full demo
full-demo: setup demo
	@echo "Demo complete ✓"
