import pandas as pd
import numpy as np
from datetime import datetime
import os

def generate_absa_robust_data(output_path="/opt/airflow/ingestion/raw_absa_historical.csv"):
    """
    Generates high-fidelity synthetic financial data for Absa Bank Kenya (2020-2025).
    """
    periods = []
    for year in range(2020, 2026):
        for q in range(1, 5):
            if year == 2025 and q > 1: break
            periods.append(f"{year}-Q{q}")

    data = []
    base_nii = 22000
    base_assets = 350000
    base_equity = 45000
    base_deposits = 250000
    base_loans = 200000

    for i, period in enumerate(periods):
        year = int(period.split("-")[0])
        growth_factor = 1 + (0.02 * i)
        noise = np.random.normal(0, 0.01)
        digital_adoption = min(95.0, 75.0 + (i * 1.2))
        opex_surge = 1.15 if year <= 2021 else 1.0
        
        nii = base_nii * growth_factor * (1 + noise)
        assets = base_assets * growth_factor * (1 + noise)
        equity = base_equity * growth_factor * (1 + noise)
        deposits = base_deposits * growth_factor * (1 + noise)
        loans = base_loans * growth_factor * (1 + noise)
        
        npl_ratio = 0.07 + (0.005 if year == 2020 else 0)
        npl_amount = loans * npl_ratio * (1 + noise)
        
        total_income = nii * 1.4
        net_income = total_income * 0.35
        opex = (total_income * 0.5) * opex_surge
        
        retail_loans = loans * 0.4
        sme_loans = loans * 0.15 * (1 + (i * 0.01))
        
        capital = equity * 0.65
        rwa = assets * 0.55

        row_metrics = {
            "Net Interest Income": nii,
            "Net Income": net_income,
            "Average Earning Assets": assets,
            "Average Shareholders Equity": equity,
            "Operating Expenses": opex,
            "Total Operating Income": total_income,
            "Non-Performing Loans": npl_amount,
            "Gross Loans": loans,
            "Total Capital": capital,
            "Risk-Weighted Assets": rwa,
            "Total Deposits": deposits,
            "Retail Loans": retail_loans,
            "SME Loans": sme_loans,
            "Digital Channel Transactions (%)": digital_adoption
        }
        
        for m_name, m_val in row_metrics.items():
            data.append({
                "metric_name": m_name,
                "period": period,
                "value": round(m_val, 2),
                "extracted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} records in {output_path}")

if __name__ == "__main__":
    generate_absa_robust_data()
