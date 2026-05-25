.PHONY: up down dbt-run-financials dbt-run-mpesa

up:
	docker compose up -d

down:
	docker compose down

dbt-run-financials:
	docker compose exec airflow bash -c "cd /opt/airflow/projects/financials/dbt && dbt run --profiles-dir ."

dbt-run-mpesa:
	docker compose exec airflow bash -c "cd /opt/airflow/projects/mpesa/dbt && dbt run --profiles-dir ."
