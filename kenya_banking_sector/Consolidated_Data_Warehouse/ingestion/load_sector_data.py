import pandas as pd
from sqlalchemy import create_engine, text
import os

def load_sector_data(project_dir="/opt/airflow/projects/sector_dwh"):
    csv_path = f"{project_dir}/ingestion/cbk_returns_consolidated.csv"
    engine = create_engine('postgresql://sector_admin:sector_password@postgres:5432/sector_dwh')
    
    if not os.path.exists(csv_path):
        # Local path fallback
        csv_path = "Kenya_Banking_Sector/Consolidated_Data_Warehouse/ingestion/cbk_returns_consolidated.csv"
        engine = create_engine('postgresql://sector_admin:sector_password@localhost:5437/sector_dwh')

    df = pd.read_csv(csv_path)
    
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS raw_cbk_returns CASCADE"))
    
    df.to_sql('raw_cbk_returns', engine, if_exists='replace', index=False)
    print("Loaded consolidated sector returns to Postgres.")

if __name__ == "__main__":
    load_sector_data()
