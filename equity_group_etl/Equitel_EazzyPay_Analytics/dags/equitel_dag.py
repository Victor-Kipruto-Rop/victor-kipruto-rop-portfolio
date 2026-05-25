from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

# Refined project mapping
sys.path.insert(0, '/opt/airflow/projects/equitel/ingestion')

from generate_equitel_data import generate_equitel_data

default_args = {
    'owner': 'equity_data_team',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

def run_ingestion():
    generate_equitel_data(output_dir='/opt/airflow/projects/equitel/ingestion')

with DAG(
    'equitel_eazzypay_analytics_dag',
    default_args=default_args,
    schedule_interval='@monthly',
    catchup=False
) as dag:

    ingest_task = PythonOperator(
        task_id='generate_synthetic_data',
        python_callable=run_ingestion,
    )

    dbt_run = BashOperator(
        task_id='dbt_run_equitel',
        bash_command='cd /opt/airflow/projects/equitel/dbt && dbt run --profiles-dir .',
    )

    ingest_task >> dbt_run
