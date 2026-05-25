.PHONY: up down dbt-run-kpi dbt-run-api test-kpi test-api

up:
	docker compose up -d

down:
	docker compose down

dbt-run-kpi:
	docker compose exec airflow bash -c "cd /opt/airflow/projects/kpi/dbt && dbt run --profiles-dir ."

dbt-run-api:
	docker compose exec airflow bash -c "cd /opt/airflow/projects/api/dbt && dbt run --profiles-dir ."

dbt-seed-kpi:
	docker compose exec airflow bash -c "cd /opt/airflow/projects/kpi/dbt && dbt seed --profiles-dir ."

dbt-seed-api:
	docker compose exec airflow bash -c "cd /opt/airflow/projects/api/dbt && dbt seed --profiles-dir ."

test-kpi:
	docker compose exec airflow pytest /opt/airflow/projects/kpi/tests/

test-api:
	docker compose exec airflow pytest /opt/airflow/projects/api/tests/
