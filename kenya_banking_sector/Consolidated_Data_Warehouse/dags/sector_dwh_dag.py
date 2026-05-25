from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'kenya_banking_sector_dwh',
    default_args=default_args,
    description='Consolidated Kenya Banking Sector Data Warehouse',
    schedule_interval='0 9 * * *',
    catchup=False,
) as dag:

    generate_data = BashOperator(
        task_id='generate_sector_data',
        bash_command='python3 /opt/airflow/projects/sector_dwh/ingestion/generate_sector_data.py',
    )

    load_data = BashOperator(
        task_id='load_sector_to_postgres',
        bash_command='python3 /opt/airflow/projects/sector_dwh/ingestion/load_sector_data.py',
    )

    dbt_run = BashOperator(
        task_id='dbt_run_sector_dwh',
        bash_command='cd /opt/airflow/projects/sector_dwh/dbt && dbt run --profiles-dir .',
    )

    generate_data >> load_data >> dbt_run
