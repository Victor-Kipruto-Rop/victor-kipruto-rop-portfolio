import pandas as pd
import os
from sqlalchemy import create_engine, text

def ingest_itc_trademap_export(project_dir=None):
    """
    Parses and ingests a manual CSV export from the ITC TradeMap Beta portal.
    URL: https://beta.trademap.org/Country_SelProduct_TS.aspx?nvpm=1|404||||TOTAL|||2|1|1|1|2|1|1|1|1|1
    """
    if project_dir is None:
        if os.path.exists("/opt/airflow/projects/kra"):
            project_dir = "/opt/airflow/projects/kra/Customs_Trade_Pipeline"
        else:
            project_dir = "KRA(DATA ENGINEERING)/Customs_Trade_Pipeline"
            
    # Search for any file containing 'TradeMap' in the ingestion folder
    ingestion_dir = os.path.join(project_dir, "ingestion")
    target_file = None
    for f in os.listdir(ingestion_dir):
        if "TradeMap" in f and f.endswith(".csv"):
            target_file = os.path.join(ingestion_dir, f)
            break
            
    if not target_file:
        print("--- ACTION REQUIRED ---")
        print("1. Visit: https://beta.trademap.org/Country_SelProduct_TS.aspx?nvpm=1|404||||TOTAL|||2|1|1|1|2|1|1|1|1|1")
        print("2. Log in (Free for Kenyan users).")
        print("3. Click 'Download' -> 'CSV'.")
        print(f"4. Save the file in '{ingestion_dir}' with 'TradeMap' in the filename.")
        return

    print(f"Processing ITC TradeMap export: {target_file}")
    
    # ITC exports often have metadata rows at the top (skip first 7-10 rows usually)
    # We'll use a dynamic header detection
    try:
        df = pd.read_csv(target_file, skiprows=10) # Adjust based on actual export
        if 'Code' not in df.columns:
            df = pd.read_csv(target_file, skiprows=5)
            
        # Clean columns: 'Code' -> hs_code, 'Product label' -> commodity, 'Value in 2023' -> declared_value
        # Note: Actual column names may vary based on the year
        year_cols = [c for c in df.columns if "Value in" in str(c)]
        if not year_cols:
            print("Could not find Value columns in TradeMap export.")
            return
            
        latest_year_col = year_cols[-1]
        year_val = int(latest_year_col.split()[-1])
        
        df_final = pd.DataFrame()
        df_final['hs_code'] = df['Code'].astype(str)
        df_final['commodity'] = df['Product label']
        df_final['origin_country'] = "World" # Benchmarks are usually global
        df_final['year'] = year_val
        df_final['volume_tons'] = 0 # Volume is often in a separate export
        
        # Value in TradeMap is usually in '000 USD, convert to M KES
        df_final['declared_value_m_kes'] = (df[latest_year_col] * 1000 * 130) / 1000000
        
        # Simulated metrics for matching our DWH schema
        df_final['duty_collected_m_kes'] = df_final['declared_value_m_kes'] * 0.25
        df_final['risk_score'] = 5.0
        
        # Ingest to DB
        engine = create_engine('postgresql://kra_admin:kra_password@postgres-kra:5432/kra_warehouse')
        if not os.path.exists("/.dockerenv"):
            engine = create_engine('postgresql://kra_admin:kra_password@localhost:5438/kra_warehouse')

        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS raw_itc_benchmarks CASCADE"))
        
        df_final.to_sql('raw_itc_benchmarks', engine, if_exists='replace', index=False)
        print(f"Successfully ingested {len(df_final)} ITC TradeMap benchmarks.")
        
    except Exception as e:
        print(f"Error parsing ITC export: {e}")

if __name__ == "__main__":
    ingest_itc_trademap_export()
