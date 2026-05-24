import pandas as pd
from sqlalchemy import create_engine
import os
import sys

# Project paths
project_dir = "/opt/airflow/projects/pan_africa"
sys.path.append(f"{project_dir}/ingestion")
sys.path.append(f"{project_dir}/forex")

from generate_subsidiary_data import generate_subsidiary_data
from fx_normalizer import FXNormalizer

def run_pan_africa_ingestion():
    output_dir = f"{project_dir}/ingestion"
    generate_subsidiary_data(output_dir=output_dir)
    
    # Run Normalization
    df = pd.read_csv(f"{output_dir}/subsidiary_financials.csv")
    normalizer = FXNormalizer()
    
    results = df.apply(lambda row: normalizer.normalize(row['net_profit'], row['currency']), axis=1)
    df['profit_usd'] = [r['usd'] for r in results]
    df['profit_kes'] = [r['kes'] for r in results]
    
    engine = create_engine('postgresql://equity_admin:equity_password@postgres/pan_africa_platform')
    df.to_sql('raw_subsidiary_financials', engine, if_exists='replace', index=False)
    print("Successfully ingested and normalized Pan-Africa data.")

if __name__ == "__main__":
    run_pan_africa_ingestion()
