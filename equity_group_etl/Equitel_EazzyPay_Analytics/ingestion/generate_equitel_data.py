import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_equitel_data(output_dir="/opt/airflow/projects/equitel/ingestion"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    periods = []
    start_date = datetime(2020, 1, 1)
    for i in range(24): # 24 months
        periods.append((start_date + timedelta(days=31*i)).strftime("%Y-%m"))

    # 1. Subscriber Data (MVNO)
    sub_data = []
    base_subs = 1500000
    for i, period in enumerate(periods):
        growth = 1 + (0.015 * i) # 1.5% monthly growth
        subs = int(base_subs * growth * np.random.normal(1, 0.005))
        sub_data.append({"period": period, "subscribers": subs, "operator": "Equitel"})
    
    pd.DataFrame(sub_data).to_csv(f"{output_dir}/equitel_subscribers.csv", index=False)

    # 2. EazzyPay & Product Cross-Sell
    txn_data = []
    base_vol = 500000000 # 500M KES
    for i, period in enumerate(periods):
        adoption_factor = 1 + (0.05 * i)
        vol = base_vol * adoption_factor * np.random.normal(1, 0.02)
        txns = int(vol / 1500)
        
        # Cross-sell metrics
        insurance_users = int(base_subs * (0.05 + (i * 0.002)) * np.random.normal(1, 0.01))
        investment_users = int(base_subs * (0.02 + (i * 0.001)) * np.random.normal(1, 0.01))
        
        txn_data.append({
            "period": period, 
            "transaction_volume": round(vol, 2), 
            "transaction_count": txns,
            "insurance_subscribers": insurance_users,
            "investment_subscribers": investment_users,
            "product": "EazzyPay"
        })
    
    pd.DataFrame(txn_data).to_csv(f"{output_dir}/eazzypay_transactions.csv", index=False)
    print(f"Generated Equitel & EazzyPay data in {output_dir}")

if __name__ == "__main__":
    generate_equitel_data()
