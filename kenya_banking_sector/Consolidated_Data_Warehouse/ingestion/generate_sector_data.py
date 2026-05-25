import pandas as pd
import numpy as np
import os
from datetime import datetime

def generate_consolidated_banking_data(output_dir=None):
    if output_dir is None:
        if os.path.exists("/opt/airflow/projects/sector_dwh"):
            output_dir = "/opt/airflow/projects/sector_dwh/ingestion"
        else:
            output_dir = "Kenya_Banking_Sector/Consolidated_Data_Warehouse/ingestion"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load bank registry
    registry_path = os.path.join(output_dir, "../seeds/bank_registry.csv")
    if os.path.exists(registry_path):
        banks_df = pd.read_csv(registry_path)
        banks = banks_df['bank_id'].tolist()
    else:
        banks = ["KCB", "EQTY", "ABSA", "COOP", "SBIC", "SCBK", "DTBK", "I&M", "NCBA"]

    years = range(2015, 2026)
    data = []
    
    for bank in banks:
        # Assign scale based on bank (Tier 1 vs others)
        is_tier1 = bank in ["KCB", "EQTY", "ABSA", "COOP", "SBIC", "SCBK", "DTBK", "I&M", "NCBA"]
        scale = np.random.uniform(500000, 1500000) if is_tier1 else np.random.uniform(50000, 500000)
        
        base_assets = scale
        for year in years:
            growth = 1 + np.random.uniform(0.05, 0.15)
            assets = base_assets * growth
            liabilities = assets * np.random.uniform(0.85, 0.90)
            equity = assets - liabilities
            loans = assets * np.random.uniform(0.5, 0.7)
            deposits = liabilities * np.random.uniform(0.9, 0.95)
            
            interest_income = loans * np.random.uniform(0.08, 0.12)
            interest_expense = deposits * np.random.uniform(0.02, 0.04)
            nii = interest_income - interest_expense
            non_int_income = nii * np.random.uniform(0.3, 0.5)
            opex = (nii + non_int_income) * np.random.uniform(0.45, 0.55)
            profit_bt = (nii + non_int_income) - opex
            profit_at = profit_bt * 0.7 # 30% tax
            
            npl_ratio = np.random.uniform(8.0, 18.0)
            car = np.random.uniform(14.5, 22.0)
            
            metrics = {
                "A1": assets,
                "A2": liabilities,
                "E1": equity,
                "P1": interest_income,
                "P2": interest_expense,
                "P3": nii,
                "P4": non_int_income,
                "P5": opex,
                "P6": profit_bt,
                "P7": profit_at,
                "L1": loans,
                "D1": deposits,
                "R1": npl_ratio,
                "C1": car
            }
            
            for code, value in metrics.items():
                data.append({
                    "bank_id": bank,
                    "year": year,
                    "return_code": code,
                    "value": round(value, 2),
                    "reported_date": f"{year}-12-31"
                })
            
            base_assets = assets
            
    df = pd.DataFrame(data)
    df.to_csv(f"{output_dir}/cbk_returns_consolidated.csv", index=False)
    print(f"Generated consolidated banking data in {output_dir}")

if __name__ == "__main__":
    generate_consolidated_banking_data()
