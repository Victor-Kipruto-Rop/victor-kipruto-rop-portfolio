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
    'kra_vat_compliance_pipeline',
    default_args=default_args,
    description='KRA VAT Compliance & Gap Analysis ETL',
    schedule_interval='0 11 * * *',
    catchup=False,
) as dag:

    generate_data = BashOperator(
        task_id='generate_vat_data',
        bash_command='python3 /opt/airflow/projects/kra/VAT_Compliance_Gap_Analysis/ingestion/generate_vat_data.py',
    )

    load_data = BashOperator(
        task_id='load_vat_to_postgres',
        bash_command='python3 /opt/airflow/projects/kra/VAT_Compliance_Gap_Analysis/ingestion/load_vat_data.py',
    )

    dbt_run = BashOperator(
        task_id='dbt_run_vat',
        bash_command='cd /opt/airflow/projects/kra/VAT_Compliance_Gap_Analysis/dbt && dbt run --profiles-dir .',
    )

    generate_data >> load_data >> dbt_run
