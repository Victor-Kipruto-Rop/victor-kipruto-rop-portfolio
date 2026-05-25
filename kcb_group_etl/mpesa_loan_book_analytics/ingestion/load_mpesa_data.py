import pandas as pd
from sqlalchemy import create_engine, text
import os

def load_mpesa_loans(project_dir="/opt/airflow/projects/mpesa"):
    csv_path = f"{project_dir}/ingestion/kcb_mpesa_loan_book.csv"
    engine = create_engine('postgresql://kcb_admin:kcb_password@postgres:5432/kcb_mpesa')
    
    df = pd.read_csv(csv_path)
    
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS raw_kcb_mpesa_loans CASCADE"))
    
    df.to_sql('raw_kcb_mpesa_loans', engine, if_exists='replace', index=False)
    print("Loaded KCB M-Pesa loans to Postgres.")

if __name__ == "__main__":
    load_mpesa_loans()
