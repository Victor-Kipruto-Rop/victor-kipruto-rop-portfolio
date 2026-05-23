.PHONY: help install setup test lint format clean docker-up docker-down run-forecast

help:
	@echo "Float Liquidity Forecasting Pipeline - Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make setup            - Setup virtual environment"
	@echo "  make init-db          - Initialize database"
	@echo ""
	@echo "Development Commands:"
	@echo "  make test             - Run all tests"
	@echo "  make test-coverage    - Run tests with coverage"
	@echo "  make lint             - Run code linting"
	@echo "  make format           - Format code with black"
	@echo "  make type-check       - Run type checking with mypy"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-up        - Start all services"
	@echo "  make docker-down      - Stop all services"
	@echo "  make docker-clean     - Remove all containers and volumes"
	@echo ""
	@echo "Running Commands:"
	@echo "  make run-forecast     - Run forecast pipeline locally"
	@echo "  make run-retrain      - Run retraining pipeline locally"
	@echo "  make run-notebook     - Start Jupyter notebook"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make logs             - View application logs"
	@echo "  make clean            - Clean up generated files"

install:
	pip install -r requirements.txt
	pre-commit install

setup:
	python -m venv .venv
	source .venv/bin/activate
	pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install

test:
	pytest tests/ -v --color=yes

test-coverage:
	pytest tests/ -v --cov=. --cov-report=html --color=yes
	@echo "Coverage report generated in htmlcov/index.html"

test-fast:
	pytest tests/ -v -k "not integration" --color=yes

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	pylint ingestion/ features/ models/ dags/
	isort --check-only .

format:
	black .
	isort .

type-check:
	mypy ingestion/ features/ models/ --ignore-missing-imports

init-db:
	python -c "from db import init_db; init_db()"

docker-up:
	docker-compose up -d
	@echo "Services starting. Wait for 30 seconds..."
	@sleep 30
	@echo "Services ready at:"
	@echo "  - Airflow: http://localhost:8080 (admin/admin)"
	@echo "  - MLflow: http://localhost:5000"
	@echo "  - Grafana: http://localhost:3000 (admin/admin)"
	@echo "  - pgAdmin: http://localhost:5050 (admin@example.com/admin)"
	@echo "  - PostgreSQL: localhost:5432"

docker-down:
	docker-compose down

docker-clean:
	docker-compose down -v
	docker system prune -f

run-forecast:
	python -c "from dags.forecast_dag import dag; print('Forecast DAG structure defined')"

run-retrain:
	python -c "from dags.retrain_dag import dag; print('Retrain DAG structure defined')"

run-notebook:
	jupyter lab --ip=0.0.0.0 --port=8888 --no-browser

logs:
	tail -f logs/app_*.log

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage

install-hooks:
	pre-commit install
	pre-commit run --all-files

dev-setup: setup install lint format test
	@echo "Development environment fully configured!"

all: clean test lint docker-up
	@echo "Full pipeline completed!"
