from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os
import pandas as pd
from sqlalchemy import create_engine

# Refined project mapping
sys.path.insert(0, '/opt/airflow/projects/pan_africa/ingestion')
sys.path.insert(0, '/opt/airflow/projects/pan_africa/forex')

from generate_subsidiary_data import generate_subsidiary_data
from fx_normalizer import FXNormalizer

default_args = {
    'owner': 'equity_data_team',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

def run_ingestion():
    output_dir = '/opt/airflow/projects/pan_africa/ingestion'
    generate_subsidiary_data(output_dir=output_dir)
    
    # Run Normalization
    df = pd.read_csv(f"{output_dir}/subsidiary_financials.csv")
    normalizer = FXNormalizer()
    
    results = df.apply(lambda row: normalizer.normalize(row['net_profit'], row['currency']), axis=1)
    df['profit_usd'] = [r['usd'] for r in results]
    df['profit_kes'] = [r['kes'] for r in results]
    
    engine = create_engine('postgresql://equity_admin:equity_password@postgres/pan_africa_platform')
    df.to_sql('raw_subsidiary_financials', engine, if_exists='replace', index=False)

with DAG(
    'equity_group_pan_africa_dag',
    default_args=default_args,
    schedule_interval='@quarterly',
    catchup=False
) as dag:

    ingest_task = PythonOperator(
        task_id='ingest_and_normalize',
        python_callable=run_ingestion,
    )

    dbt_run = BashOperator(
        task_id='dbt_run_pan_africa',
        bash_command='cd /opt/airflow/projects/pan_africa/dbt && dbt run --profiles-dir .',
    )

    ingest_task >> dbt_run
