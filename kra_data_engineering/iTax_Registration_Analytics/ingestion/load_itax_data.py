import pandas as pd
from sqlalchemy import create_engine, text
import os

def load_itax_data(project_dir=None):
    if project_dir is None:
        if os.path.exists("/opt/airflow/projects/kra"):
            project_dir = "/opt/airflow/projects/kra/iTax_Registration_Analytics"
        else:
            project_dir = "KRA(DATA ENGINEERING)/iTax_Registration_Analytics"
            
    csv_path = os.path.join(project_dir, "ingestion/itax_registrations.csv")
    
    engine = create_engine('postgresql://kra_admin:kra_password@postgres-kra:5432/kra_warehouse')
    if not os.path.exists("/.dockerenv"):
        engine = create_engine('postgresql://kra_admin:kra_password@localhost:5438/kra_warehouse')

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS raw_itax_registrations CASCADE"))
    
    df.to_sql('raw_itax_registrations', engine, if_exists='replace', index=False)
    print(f"Loaded iTax registration data from {csv_path} to Postgres.")

if __name__ == "__main__":
    load_itax_data()
