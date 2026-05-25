.PHONY: up down dbt-run load-data generate-data

up:
	docker compose up -d

down:
	docker compose down

generate-data:
	python3 ingestion/generate_sector_data.py

load-data:
	python3 ingestion/load_sector_data.py

dbt-run:
	docker compose exec airflow bash -c "cd /opt/airflow/projects/sector_dwh/dbt && dbt run --profiles-dir ."
