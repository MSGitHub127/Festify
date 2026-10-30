.PHONY: help install lint test run docker-build docker-run clean

help:
	@echo "Festify Developer Commands:"
	@echo "  make install      Install Python application and development dependencies"
	@echo "  make lint         Run Ruff automated code quality and linting checks"
	@echo "  make test         Execute full pytest automated test suite with coverage"
	@echo "  make run          Launch local development FastAPI server with hot-reload"
	@echo "  make docker-build Build hardened multi-stage production Docker image"
	@echo "  make docker-run   Run production container locally on port 8000"
	@echo "  make clean        Remove cache directories, build artifacts, and temp files"

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

lint:
	ruff check .

test:
	pytest -v --cov=app --cov-report=term-missing tests/

run:
	uvicorn app.main:app --reload --port 8000

docker-build:
	docker build -t festify:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env.example festify:latest

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__ htmlcov .coverage
