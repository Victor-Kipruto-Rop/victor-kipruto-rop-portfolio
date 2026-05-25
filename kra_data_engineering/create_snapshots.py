import pandas as pd
from sqlalchemy import create_engine
import os

def create_kra_snapshots():
    try:
        # Check if running inside Docker
        if os.path.exists("/.dockerenv"):
            host = "postgres-kra"
            port = "5432"
            project_root = "/opt/airflow/projects/kra"
        else:
            host = "localhost"
            port = "5438"
            project_root = "KRA(DATA ENGINEERING)"
            
        engine = create_engine(f'postgresql://kra_admin:kra_password@{host}:{port}/kra_warehouse')
        
        # Define tables to snapshot for each project
        snapshots = {
            "Tax_Revenue_Analytics": ["mart_revenue_by_tax_head", "mart_target_vs_actual"],
            "Customs_Trade_Pipeline": ["mart_duty_collection", "mart_trade_balance", "mart_trade_by_hs_code"],
            "VAT_Compliance_Gap_Analysis": ["mart_vat_gap_by_sector"],
            "iTax_Registration_Analytics": ["mart_registrations_summary"]
        }
        
        for project, tables in snapshots.items():
            snapshot_dir = os.path.join(project_root, project, "dashboards/snapshots")
            os.makedirs(snapshot_dir, exist_ok=True)
            
            for table in tables:
                df = pd.read_sql(f"SELECT * FROM {table}", engine)
                csv_path = os.path.join(snapshot_dir, f"{table}.csv")
                df.to_csv(csv_path, index=False)
                print(f"Snapshot created: {csv_path}")
                
    except Exception as e:
        print(f"Error creating snapshots: {e}")

if __name__ == "__main__":
    create_kra_snapshots()
