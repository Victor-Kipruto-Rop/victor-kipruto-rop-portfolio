from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add ingestion to path
sys.path.insert(0, '/opt/airflow/projects/api/ingestion')

# Mock import for structure
# from scheduled_sync import sync_transactions

default_args = {
    'owner': 'absa_api_team',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

def trigger_sync():
    print("Triggering Open Banking API sync...")

with DAG(
    'absa_open_banking_sync',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    sync_task = PythonOperator(
        task_id='sync_transactions',
        python_callable=trigger_sync,
    )
