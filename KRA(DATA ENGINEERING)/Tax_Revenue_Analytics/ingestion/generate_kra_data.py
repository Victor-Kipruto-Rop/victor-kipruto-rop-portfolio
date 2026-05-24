import pandas as pd
import numpy as np
import os
from datetime import datetime

def generate_kra_revenue_data(output_dir=None):
    if output_dir is None:
        if os.path.exists("/opt/airflow/projects/kra_revenue"):
            output_dir = "/opt/airflow/projects/kra_revenue/ingestion"
        else:
            output_dir = "KRA(DATA ENGINEERING)/Tax_Revenue_Analytics/ingestion"
            
    os.makedirs(output_dir, exist_ok=True)
    
    tax_heads = ["Income Tax", "VAT", "Excise Duty", "Customs & Border Control", "Other Taxes"]
    years = range(2010, 2026)
    months = range(1, 13)
    
    data = []
    
    for year in years:
        for month in months:
            base_revenue = 50000 + (year - 2010) * 10000
            for head in tax_heads:
                seasonality = 1 + 0.1 * np.sin(2 * np.pi * month / 12)
                growth = 1 + np.random.uniform(0.05, 0.12)
                actual_revenue = base_revenue * seasonality * growth * np.random.uniform(0.8, 1.2)
                target_revenue = base_revenue * seasonality * growth * 1.05
                
                data.append({
                    "tax_head": head,
                    "year": year,
                    "month": month,
                    "actual_revenue_m_kes": round(actual_revenue, 2),
                    "target_revenue_m_kes": round(target_revenue, 2),
                    "reported_date": f"{year}-{month:02d}-28"
                })
                
    df = pd.DataFrame(data)
    csv_path = os.path.join(output_dir, "kra_revenue_performance.csv")
    df.to_csv(csv_path, index=False)
    print(f"Generated KRA revenue data in {csv_path}")

if __name__ == "__main__":
    generate_kra_revenue_data()
