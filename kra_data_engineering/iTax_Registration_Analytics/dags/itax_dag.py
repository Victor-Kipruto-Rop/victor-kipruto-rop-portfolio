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
    'kra_itax_registration_pipeline',
    default_args=default_args,
    description='KRA iTax Registration Analytics ETL',
    schedule_interval='0 12 * * *',
    catchup=False,
) as dag:

    generate_data = BashOperator(
        task_id='generate_itax_data',
        bash_command='python3 /opt/airflow/projects/kra/iTax_Registration_Analytics/ingestion/generate_itax_data.py',
    )

    load_data = BashOperator(
        task_id='load_itax_to_postgres',
        bash_command='python3 /opt/airflow/projects/kra/iTax_Registration_Analytics/ingestion/load_itax_data.py',
    )

    dbt_run = BashOperator(
        task_id='dbt_run_itax',
        bash_command='cd /opt/airflow/projects/kra/iTax_Registration_Analytics/dbt && dbt run --profiles-dir .',
    )

    generate_data >> load_data >> dbt_run
