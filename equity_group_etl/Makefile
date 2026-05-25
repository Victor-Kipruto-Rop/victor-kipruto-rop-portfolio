.PHONY: up down dbt-run-equitel dbt-run-pan-africa test-equitel test-pan-africa

up:
	docker compose up -d

down:
	docker compose down

dbt-run-equitel:
	docker compose exec airflow bash -c "cd /opt/airflow/projects/equitel/dbt && dbt run --profiles-dir ."

dbt-run-pan-africa:
	docker compose exec airflow bash -c "cd /opt/airflow/projects/pan_africa/dbt && dbt run --profiles-dir ."

test-equitel:
	docker compose exec airflow pytest /opt/airflow/projects/equitel/tests/

test-pan-africa:
	docker compose exec airflow pytest /opt/airflow/projects/pan_africa/tests/
