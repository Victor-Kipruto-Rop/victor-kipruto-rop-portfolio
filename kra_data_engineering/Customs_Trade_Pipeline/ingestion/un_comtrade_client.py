import pandas as pd
import os
from sqlalchemy import create_engine, text

def ingest_un_comtrade_data(project_dir=None):
    if project_dir is None:
        if os.path.exists("/opt/airflow/projects/kra"):
            project_dir = "/opt/airflow/projects/kra/Customs_Trade_Pipeline"
        else:
            project_dir = "KRA(DATA ENGINEERING)/Customs_Trade_Pipeline"
            
    # File paths
    csv_path = "KRA(DATA ENGINEERING)/TradeData_5_24_2026_20_20_4.csv"
    xlsx_path = "KRA(DATA ENGINEERING)/TradeData.xlsx"
    
    # Internal Docker connection
    engine = create_engine('postgresql://kra_admin:kra_password@postgres-kra:5432/kra_warehouse')
    if not os.path.exists("/.dockerenv"):
        # Local connection
        engine = create_engine('postgresql://kra_admin:kra_password@localhost:5438/kra_warehouse')

    # Load CSV (with encoding handling for international characters)
    if os.path.exists(csv_path):
        try:
            df_csv = pd.read_csv(csv_path, encoding='utf-8')
        except UnicodeDecodeError:
            df_csv = pd.read_csv(csv_path, encoding='latin1')
        print(f"Loaded {len(df_csv)} records from {csv_path}")
    else:
        print(f"Warning: {csv_path} not found.")
        df_csv = pd.DataFrame()

    # Load XLSX
    if os.path.exists(xlsx_path):
        df_xlsx = pd.read_excel(xlsx_path)
        print(f"Loaded {len(df_xlsx)} records from {xlsx_path}")
    else:
        print(f"Warning: {xlsx_path} not found.")
        df_xlsx = pd.DataFrame()

    # Combine data
    df_combined = pd.concat([df_csv, df_xlsx], ignore_index=True).drop_duplicates()
    
    if not df_combined.empty:
        # Standardize columns to match our dbt/DWH expectations
        df_final = pd.DataFrame()
        df_final['hs_code'] = df_combined['cmdCode'].astype(str)
        df_final['commodity'] = df_combined['cmdDesc']
        df_final['origin_country'] = df_combined['reporterDesc']
        df_final['year'] = df_combined['refYear'].astype(int)
        df_final['volume_tons'] = df_combined['netWgt'].fillna(0) / 1000 # weight to tons
        
        # primaryValue is in USD, convert to KES (130) then to M KES
        df_final['declared_value_m_kes'] = (df_combined['primaryValue'] * 130) / 1000000
        
        # Simulated metrics for benchmarks
        df_final['duty_collected_m_kes'] = df_final['declared_value_m_kes'] * 0.25 * 0.95
        df_final['risk_score'] = 10.0
        
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS raw_un_comtrade_benchmarks CASCADE"))
        
        df_final.to_sql('raw_un_comtrade_benchmarks', engine, if_exists='replace', index=False)
        print(f"Ingested {len(df_final)} UN Comtrade benchmarks into PostgreSQL.")
    else:
        print("No data found to ingest.")

if __name__ == "__main__":
    ingest_un_comtrade_data()
