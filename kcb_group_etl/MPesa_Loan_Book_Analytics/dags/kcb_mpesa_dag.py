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
    'kcb_mpesa_pipeline',
    default_args=default_args,
    description='KCB M-Pesa Loan Book Analysis ETL',
    schedule_interval='30 8 * * *',
    catchup=False,
) as dag:

    generate_data = BashOperator(
        task_id='generate_mpesa_data',
        bash_command='python3 /opt/airflow/projects/mpesa/ingestion/generate_mpesa_data.py',
    )

    load_data = BashOperator(
        task_id='load_mpesa_to_postgres',
        bash_command='python3 /opt/airflow/projects/mpesa/ingestion/load_mpesa_data.py',
    )

    dbt_run = BashOperator(
        task_id='dbt_run_mpesa',
        bash_command='cd /opt/airflow/projects/mpesa/dbt && dbt run --profiles-dir .',
    )

    generate_data >> load_data >> dbt_run
