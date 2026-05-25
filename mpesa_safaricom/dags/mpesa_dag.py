from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'mpesa_flagship_pipeline',
    default_args=default_args,
    description='Orchestrates M-Pesa transaction processing and dbt transformations',
    schedule_interval=timedelta(hours=1),
    catchup=False,
    doc_md="""
    ## M-Pesa Flagship Pipeline
    This DAG manages the hourly batch processing layer for M-Pesa transactions.
    1. **dbt_run**: Materializes intermediate and mart tables.
    2. **dbt_test**: Validates data quality constraints.
    3. **slack_alert**: Notifies on pipeline status.
    """
) as dag:

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/dbt && dbt run --profiles-dir .',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/airflow/dbt && dbt test --profiles-dir .',
    )

    dbt_run >> dbt_test
