import pandas as pd
from sqlalchemy import create_engine, text
import os

def load_equitel_data(project_dir="/opt/airflow/projects/equitel"):
    ingestion_dir = f"{project_dir}/ingestion"
    engine = create_engine('postgresql://equity_admin:equity_password@postgres/equitel_analytics')
    
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS raw_equitel_subscribers CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS raw_eazzypay_transactions CASCADE"))

    # 1. Subscribers
    df_sub = pd.read_csv(f"{ingestion_dir}/equitel_subscribers.csv")
    df_sub.to_sql('raw_equitel_subscribers', engine, if_exists='replace', index=False)
    
    # 2. EazzyPay
    df_txn = pd.read_csv(f"{ingestion_dir}/eazzypay_transactions.csv")
    df_txn.to_sql('raw_eazzypay_transactions', engine, if_exists='replace', index=False)
    
    print("Successfully loaded Equitel & EazzyPay data to Postgres.")

if __name__ == "__main__":
    load_equitel_data()
