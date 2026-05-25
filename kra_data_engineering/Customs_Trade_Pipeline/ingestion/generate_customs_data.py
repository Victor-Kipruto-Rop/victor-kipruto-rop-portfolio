import pandas as pd
import numpy as np
import os
from datetime import datetime

def generate_customs_data(project_dir=None):
    if project_dir is None:
        if os.path.exists("/opt/airflow/projects/kra"):
            project_dir = "/opt/airflow/projects/kra/Customs_Trade_Pipeline"
        else:
            project_dir = "KRA(DATA ENGINEERING)/Customs_Trade_Pipeline"
            
    output_dir = os.path.join(project_dir, "ingestion")
    os.makedirs(output_dir, exist_ok=True)
    
    # Load HS codes from seed if available
    hs_seeds_path = os.path.join(project_dir, "seeds/hs_codes.csv")
    if os.path.exists(hs_seeds_path):
        hs_df = pd.read_csv(hs_seeds_path)
        # Using correct column names from the actual seed file
        hs_codes = dict(zip(hs_df['hs_code'].astype(str), hs_df['commodity_description']))
    else:
        hs_codes = {"2701": "Coal", "7108": "Gold"}
    
    countries = ["China", "India", "UAE", "USA", "Netherlands", "Pakistan", "UK", "Tanzania", "Uganda"]
    years = range(2020, 2026)
    
    data = []
    
    for year in years:
        for code, desc in hs_codes.items():
            for country in countries:
                volume = np.random.uniform(50, 5000)
                unit_price = np.random.uniform(100, 500)
                if code in ["2710", "8703"]: unit_price *= 5
                if code == "7108": unit_price *= 20
                
                declared_value = volume * unit_price / 1000 
                duty_rate = 0.25 
                if code in ["3102", "3004"]: duty_rate = 0.0
                
                duty_collected = declared_value * duty_rate * np.random.uniform(0.9, 1.0)
                
                risk_score = np.random.uniform(5, 40)
                if country == "UAE" and code == "7108": risk_score = np.random.uniform(75, 98)
                
                data.append({
                    "hs_code": code,
                    "commodity": desc,
                    "origin_country": country,
                    "year": year,
                    "volume_tons": round(volume, 2),
                    "declared_value_m_kes": round(declared_value, 2),
                    "duty_collected_m_kes": round(duty_collected, 2),
                    "risk_score": round(risk_score, 2)
                })
                
    df = pd.DataFrame(data)
    csv_path = os.path.join(output_dir, "customs_declarations.csv")
    df.to_csv(csv_path, index=False)
    print(f"Generated {len(df)} Customs records in {csv_path}")

if __name__ == "__main__":
    generate_customs_data()
