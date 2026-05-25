import pandas as pd
from sqlalchemy import create_engine, text
import os

def load_customs_data(project_dir=None):
    if project_dir is None:
        if os.path.exists("/opt/airflow/projects/kra"):
            project_dir = "/opt/airflow/projects/kra/Customs_Trade_Pipeline"
        else:
            project_dir = "KRA(DATA ENGINEERING)/Customs_Trade_Pipeline"
            
    csv_path = os.path.join(project_dir, "ingestion/customs_declarations.csv")
    
    # Internal Docker connection
    engine = create_engine('postgresql://kra_admin:kra_password@postgres-kra:5432/kra_warehouse')
    
    if not os.path.exists("/.dockerenv"):
        # Local connection (outside Docker)
        engine = create_engine('postgresql://kra_admin:kra_password@localhost:5438/kra_warehouse')

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS raw_customs_declarations CASCADE"))
    
    df.to_sql('raw_customs_declarations', engine, if_exists='replace', index=False)
    print(f"Loaded Customs declarations from {csv_path} to Postgres.")

if __name__ == "__main__":
    load_customs_data()
