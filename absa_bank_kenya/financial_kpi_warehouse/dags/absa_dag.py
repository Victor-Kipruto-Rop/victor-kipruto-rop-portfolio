from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os

# Add ingestion to path
sys.path.insert(0, '/opt/airflow/projects/kpi/ingestion')

from pdf_extractor import AbsaPDFExtractor

default_args = {
    'owner': 'absa_data_team',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_extraction():
    # In a real scenario, we'd loop through downloaded PDFs
    # pdf_dir = "/opt/airflow/data/absa_reports"
    # for pdf_file in os.listdir(pdf_dir):
    #     extractor = AbsaPDFExtractor(os.path.join(pdf_dir, pdf_file))
    #     extractor.run()
    print("Running PDF extraction...")

with DAG(
    'absa_financial_kpi_dag',
    default_args=default_args,
    description='Scrapes and extracts Absa financial KPIs',
    schedule_interval='@quarterly',
    catchup=False
) as dag:

    scrape_reports = BashOperator(
        task_id='scrape_absa_reports',
        bash_command='python /opt/airflow/projects/kpi/ingestion/absa_ir_scraper.py',
    )

    extract_kpis = PythonOperator(
        task_id='extract_kpis_from_pdf',
        python_callable=run_extraction,
    )

    dbt_seed = BashOperator(
        task_id='dbt_seed',
        bash_command='cd /opt/airflow/projects/kpi/dbt && dbt seed --profiles-dir .',
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/projects/kpi/dbt && dbt run --profiles-dir .',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/airflow/projects/kpi/dbt && dbt test --profiles-dir .',
    )

    scrape_reports >> extract_kpis >> dbt_seed >> dbt_run >> dbt_test
