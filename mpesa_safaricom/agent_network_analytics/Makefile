.PHONY: help install up down lint test test-unit test-integration run-ingest run-spatial run-dag dbt-run dbt-test clean

help:			## Show this help
	@sed -n 's/^## //p' $(MAKEFILE_LIST)

install:			## Install Python dependencies
	pip install -r requirements.txt

up:				## Start docker-compose (PostGIS)
	docker compose up -d
	@echo "Waiting for PostGIS on $${MPESA_DATABASE_URL:-localhost:5433}..."
	@for i in $$(seq 1 30); do \
	  pg_isready -h localhost -p 5433 -U mpesa && break; \
	  echo "Waiting... ($$i)"; sleep 2; \
	done
	@echo "PostGIS is ready."

down:				## Stop docker-compose
	docker compose down

lint:				## Run ruff linter
	ruff check ingestion/ scripts/ spatial/ dags/ tests/ || true

test: test-unit test-integration	## Run all tests

test-unit:			## Run unit tests
	pytest tests/unit/ -v --tb=short -m "not integration"

test-integration: up		## Run integration tests (requires running PostGIS)
	pytest tests/integration/ -v --tb=short -m integration -k "not live"

run-ingest:			## Run CBK ingestion pipeline
	python3 ingestion/cbk_loader.py

run-extract:			## Run PDF extractor (CBK PDFs)
	python3 ingestion/pdf_extractor.py

run-spatial:			## Run spatial analytics
	python3 spatial/ward_analysis.py

run-placement:			## Run optimal placement suggestions
	python3 spatial/optimal_placement.py

run-aggregates:			## Build ward aggregates
	python3 scripts/create_ward_aggregates.py

export-all:			## Export all data for Kepler
	python3 scripts/export_for_kepler.py && \
	python3 scripts/export_wards_geojson.py && \
	python3 scripts/export_analysis_csv.py

dbt-run:			## Run dbt models
	dbt run --project-dir dbt --profiles-dir dbt

dbt-test:			## Run dbt tests
	dbt test --project-dir dbt --profiles-dir dbt

dbt-seed:			## Load dbt seeds
	dbt seed --project-dir dbt --profiles-dir dbt

clean:				## Remove generated data
	rm -rf data/kepler/* data/reports/* dbt/target dbt/logs
