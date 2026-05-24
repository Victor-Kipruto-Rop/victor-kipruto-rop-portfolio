import pandas as pd
from sqlalchemy import create_engine, text
import os

def load_kcb_financials(project_dir="/opt/airflow/projects/financials"):
    csv_path = f"{project_dir}/ingestion/kcb_subsidiary_financials.csv"
    engine = create_engine('postgresql://kcb_admin:kcb_password@postgres:5432/kcb_financials')
    
    df = pd.read_csv(csv_path)
    
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS raw_kcb_financials CASCADE"))
    
    df.to_sql('raw_kcb_financials', engine, if_exists='replace', index=False)
    print("Loaded KCB financials to Postgres.")

if __name__ == "__main__":
    load_kcb_financials()
