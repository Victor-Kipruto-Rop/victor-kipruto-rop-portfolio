.PHONY: up down dbt-run generate-data

up:
	docker compose up -d

down:
	docker compose down

generate-data:
	python3 ingestion/generate_customs_data.py

dbt-run:
	cd dbt && dbt run --profiles-dir .
