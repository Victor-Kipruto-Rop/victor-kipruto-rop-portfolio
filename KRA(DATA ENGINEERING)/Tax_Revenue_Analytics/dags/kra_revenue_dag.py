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
    'kra_tax_revenue_pipeline',
    default_args=default_args,
    description='KRA Tax Revenue Analytics ETL',
    schedule_interval='0 10 * * *',
    catchup=False,
) as dag:

    generate_data = BashOperator(
        task_id='generate_kra_revenue_data',
        bash_command='python3 /opt/airflow/projects/kra_revenue/ingestion/generate_kra_data.py',
    )

    load_data = BashOperator(
        task_id='load_kra_to_postgres',
        bash_command='python3 /opt/airflow/projects/kra_revenue/ingestion/load_kra_data.py',
    )

    dbt_run = BashOperator(
        task_id='dbt_run_kra_revenue',
        bash_command='cd /opt/airflow/projects/kra_revenue/dbt && dbt run --profiles-dir .',
    )

    generate_data >> load_data >> dbt_run
