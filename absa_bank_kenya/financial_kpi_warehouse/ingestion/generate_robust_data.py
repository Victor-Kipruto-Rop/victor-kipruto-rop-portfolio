import pandas as pd
import numpy as np
import os
from datetime import datetime

def generate_absa_financials(output_dir="Absa_Bank_Kenya(PIPELINE)/Financial_KPIs_Warehouse/ingestion"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Financial indicators
    indicators = [
        "Total Assets", "Net Loans", "Customer Deposits", "Shareholders Equity",
        "Net Interest Income", "Non-Interest Income", "Operating Expenses", "Profit After Tax"
    ]
    years = range(2018, 2026)
    
    data = []
    base_assets = 350000 # M KES
    
    for year in years:
        growth = 1 + np.random.uniform(0.08, 0.15)
        assets = base_assets * growth
        loans = assets * np.random.uniform(0.55, 0.65)
        deposits = assets * np.random.uniform(0.7, 0.8)
        equity = assets * np.random.uniform(0.1, 0.13)
        
        nii = loans * np.random.uniform(0.09, 0.11)
        non_int = nii * np.random.uniform(0.3, 0.45)
        opex = (nii + non_int) * np.random.uniform(0.48, 0.52)
        profit = (nii + non_int - opex) * 0.7
        
        metrics = {
            "Total Assets": assets,
            "Net Loans": loans,
            "Customer Deposits": deposits,
            "Shareholders Equity": equity,
            "Net Interest Income": nii,
            "Non-Interest Income": non_int,
            "Operating Expenses": opex,
            "Profit After Tax": profit
        }
        
        for ind, val in metrics.items():
            data.append({
                "indicator": ind,
                "year": year,
                "value_m_kes": round(val, 2),
                "reported_date": f"{year}-12-31"
            })
        base_assets = assets
            
    df = pd.DataFrame(data)
    df.to_csv(f"{output_dir}/absa_robust_financials.csv", index=False)
    print(f"Generated robust Absa financials in {output_dir}")

if __name__ == "__main__":
    generate_absa_financials()
