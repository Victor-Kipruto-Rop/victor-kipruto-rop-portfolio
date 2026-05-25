import pandas as pd
import numpy as np
import os
from datetime import datetime

def generate_equity_financials(output_dir="Equity_Group(PIPELINE_ETL)/Pan_Africa_Financial_Platform/ingestion"):
    os.makedirs(output_dir, exist_ok=True)
    
    subsidiaries = [
        "Equity Bank Kenya", "Equity Bank Uganda", "Equity Bank Tanzania",
        "Equity Bank Rwanda", "Equity Bank South Sudan", "Equity Bank Congo (DRC)",
        "Equity Bank Ethiopia (Rep Office)"
    ]
    years = range(2020, 2026)
    
    data = []
    
    for sub in subsidiaries:
        base_assets = np.random.uniform(500000, 1000000) if "Kenya" in sub or "Congo" in sub else np.random.uniform(50000, 150000)
        
        for year in years:
            growth = 1 + np.random.uniform(0.1, 0.25) # Equity grows fast
            assets = base_assets * growth
            loans = assets * np.random.uniform(0.5, 0.6)
            deposits = assets * np.random.uniform(0.75, 0.85)
            profit = assets * np.random.uniform(0.02, 0.04)
            
            data.append({
                "subsidiary": sub,
                "year": year,
                "total_assets_m_kes": round(assets, 2),
                "net_loans_m_kes": round(loans, 2),
                "customer_deposits_m_kes": round(deposits, 2),
                "profit_after_tax_m_kes": round(profit, 2),
                "npl_ratio_percent": round(np.random.uniform(5, 12), 2),
                "digital_txn_percentage": round(np.random.uniform(85, 99), 2)
            })
            base_assets = assets
            
    df = pd.DataFrame(data)
    df.to_csv(f"{output_dir}/equity_subsidiary_performance.csv", index=False)
    print(f"Generated Equity subsidiary data in {output_dir}")

if __name__ == "__main__":
    generate_equity_financials()
