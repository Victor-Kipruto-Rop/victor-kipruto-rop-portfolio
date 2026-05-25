import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_mpesa_loan_data(output_dir="/opt/airflow/projects/mpesa/ingestion"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Simulate cohorts from Jan 2022 to Dec 2023
    start_date = datetime(2022, 1, 1)
    cohorts = [ (start_date + timedelta(days=31*i)).strftime("%Y-%m") for i in range(24) ]
    
    data = []
    for cohort in cohorts:
        base_disbursed = np.random.uniform(100, 500) # Millions KES
        
        # Track repayment over 6 months for each cohort
        for month_offset in range(7):
            observation_month = (datetime.strptime(cohort, "%Y-%m") + timedelta(days=31*month_offset)).strftime("%Y-%m")
            
            # Cumulative repayment
            repayment_rate = min(0.15 * month_offset + np.random.normal(0, 0.02), 0.98)
            repaid_amt = base_disbursed * repayment_rate
            
            # Default rate increases over time
            npl_rate = 0.02 + (0.01 * month_offset) + np.random.normal(0, 0.005)
            
            data.append({
                "cohort_month": cohort,
                "observation_month": observation_month,
                "month_offset": month_offset,
                "amount_disbursed_m_kes": round(base_disbursed, 2),
                "amount_repaid_m_kes": round(repaid_amt, 2),
                "npl_amount_m_kes": round(base_disbursed * npl_rate, 2),
                "active_loans_count": int(base_disbursed * 1000 * (1 - repayment_rate))
            })
            
    df = pd.DataFrame(data)
    df.to_csv(f"{output_dir}/kcb_mpesa_loan_book.csv", index=False)
    print(f"Generated KCB M-Pesa loan book data in {output_dir}")

if __name__ == "__main__":
    generate_mpesa_loan_data()
