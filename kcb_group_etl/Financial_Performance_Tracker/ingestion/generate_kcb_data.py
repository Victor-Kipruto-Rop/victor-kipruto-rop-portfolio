import pandas as pd
import numpy as np
from datetime import datetime
import os

def generate_kcb_financials(output_dir="/opt/airflow/projects/financials/ingestion"):
    os.makedirs(output_dir, exist_ok=True)
    
    subsidiaries = [
        "KCB Bank Kenya", "KCB Bank Tanzania", "KCB Bank Uganda", 
        "KCB Bank Rwanda", "KCB Bank South Sudan", "KCB Bank Burundi", 
        "Trust Merchant Bank (DRC)"
    ]
    
    years = [2020, 2021, 2022, 2023, 2024]
    data = []
    
    for sub in subsidiaries:
        base_profit = np.random.uniform(500, 5000) if "Kenya" in sub else np.random.uniform(50, 500)
        for year in years:
            growth = 1 + np.random.uniform(-0.05, 0.15)
            profit = base_profit * growth
            assets = profit * np.random.uniform(5, 10)
            npl_ratio = np.random.uniform(0.05, 0.15)
            
            # Real-world metrics
            interest_income = assets * np.random.uniform(0.08, 0.12)
            interest_expense = interest_income * np.random.uniform(0.3, 0.5)
            net_interest_income = interest_income - interest_expense
            opex = net_interest_income * np.random.uniform(0.4, 0.6)
            equity = assets * np.random.uniform(0.1, 0.15)
            
            data.append({
                "subsidiary": sub,
                "year": year,
                "net_profit_m_kes": round(profit, 2),
                "total_assets_m_kes": round(assets, 2),
                "interest_income_m_kes": round(interest_income, 2),
                "interest_expense_m_kes": round(interest_expense, 2),
                "net_interest_income_m_kes": round(net_interest_income, 2),
                "operating_expenses_m_kes": round(opex, 2),
                "shareholders_equity_m_kes": round(equity, 2),
                "npl_ratio_percent": round(npl_ratio * 100, 2),
                "customer_count": int(assets * 100)
            })
            base_profit = profit
            
    df = pd.DataFrame(data)
    df.to_csv(f"{output_dir}/kcb_subsidiary_financials.csv", index=False)
    print(f"Generated KCB financials in {output_dir}")

if __name__ == "__main__":
    generate_kcb_financials()
