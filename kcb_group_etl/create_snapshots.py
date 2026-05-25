import pandas as pd
from sqlalchemy import create_engine
import os

def create_snapshots():
    # Connect to local Postgres (since it's running in Docker/Local)
    # Note: We use 5436 because that's the host-mapped port in docker-compose
    financials_engine = create_engine('postgresql://kcb_admin:kcb_password@localhost:5436/kcb_financials')
    mpesa_engine = create_engine('postgresql://kcb_admin:kcb_password@localhost:5436/kcb_mpesa')
    
    # Financials Project Snapshots
    financial_tables = [
        'mart_subsidiary_performance',
        'mart_nim_trend',
        'mart_roe_roa',
        'mart_subsidiary_perf'
    ]
    
    for table in financial_tables:
        df = pd.read_sql(f'SELECT * FROM {table}', financials_engine)
        path = f'KCB_Group(ETL)/Financial_Performance_Tracker/dashboards/snapshots/{table}.csv'
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
        print(f"Snapshot created: {path}")

    # M-Pesa Project Snapshots
    mpesa_tables = [
        'mart_vintage_analysis',
        'mart_loan_cohorts',
        'mart_collection_efficiency',
        'mart_vintage_performance'
    ]
    
    for table in mpesa_tables:
        df = pd.read_sql(f'SELECT * FROM {table}', mpesa_engine)
        path = f'KCB_Group(ETL)/MPesa_Loan_Book_Analytics/dashboards/snapshots/{table}.csv'
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
        print(f"Snapshot created: {path}")

if __name__ == "__main__":
    create_snapshots()
