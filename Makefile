.PHONY: help install dev test lint format clean run docker-build docker-run

help:
	@echo "AI Candidate Sourcing System - Available Commands:"
	@echo ""
	@echo "  make install       - Install production dependencies"
	@echo "  make dev           - Install development dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linting checks"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean temporary files"
	@echo "  make run           - Run API server locally"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container"
	@echo ""

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio black flake8 mypy

test:
	pytest tests/ -v

lint:
	flake8 src/ --max-line-length=120 --ignore=E501,W503
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/ --line-length=120

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov

run:
	python -m src

docker-build:
	docker build -t ai-candidate-sourcing:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f
