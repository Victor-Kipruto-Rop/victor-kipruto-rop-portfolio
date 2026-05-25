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
    'kcb_financial_pipeline',
    default_args=default_args,
    description='KCB Subsidiary Financial Performance ETL',
    schedule_interval='0 8 * * *',
    catchup=False,
) as dag:

    generate_mock_data = BashOperator(
        task_id='generate_mock_kcb_data',
        bash_command='python3 /opt/airflow/projects/financials/ingestion/generate_kcb_data.py',
    )

    ingest_real_pdf = BashOperator(
        task_id='ingest_real_pdf_fy2025',
        bash_command='python3 /opt/airflow/projects/financials/ingestion/load_real_pdf.py',
    )

    load_mock_data = BashOperator(
        task_id='load_mock_kcb_to_postgres',
        bash_command='python3 /opt/airflow/projects/financials/ingestion/load_kcb_data.py',
    )

    dbt_run = BashOperator(
        task_id='dbt_run_financials',
        bash_command='cd /opt/airflow/projects/financials/dbt && dbt run --profiles-dir .',
    )

    generate_mock_data >> load_mock_data >> ingest_real_pdf >> dbt_run
