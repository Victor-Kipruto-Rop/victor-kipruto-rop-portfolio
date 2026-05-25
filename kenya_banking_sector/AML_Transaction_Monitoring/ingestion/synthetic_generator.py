import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_aml_test_data(num_transactions=5000, output_dir="Kenya_Banking_Sector/AML_Transaction_Monitoring/data"):
    os.makedirs(output_dir, exist_ok=True)
    
    banks = ["KCB", "EQTY", "ABSA", "COOP", "SBIC", "SCBK", "DTBK", "I&M"]
    account_types = ["Personal", "Business", "SME"]
    countries = ["KE", "UG", "TZ", "RW", "AE", "UK", "US", "CH"] # Including tax havens/high-risk
    
    data = []
    
    # Generate legitimate base
    for i in range(num_transactions):
        tx_id = f"TXN_{1000000 + i}"
        bank = random.choice(banks)
        amount = np.random.exponential(50000) # Most txns are small
        
        # Inject "Structuring" pattern (Multiple txns just under 1M KES)
        if i % 100 == 0:
             # Structuring: 5 txns of 950k-990k in one day
             for j in range(5):
                 data.append({
                     "txn_id": f"{tx_id}_STR_{j}",
                     "bank_id": bank,
                     "account_id": f"ACC_{random.randint(1000, 2000)}",
                     "amount": random.randint(950000, 999000),
                     "txn_type": "Cash Deposit",
                     "country": "KE",
                     "is_pep": False,
                     "timestamp": datetime.now() - timedelta(days=random.randint(0, 30))
                 })
        
        # Inject "PEP" pattern
        is_pep = True if random.random() < 0.02 else False
        
        data.append({
            "txn_id": tx_id,
            "bank_id": bank,
            "account_id": f"ACC_{random.randint(1000, 5000)}",
            "amount": round(amount, 2),
            "txn_type": random.choice(["Transfer", "Cash Deposit", "Wire"]),
            "country": random.choices(countries, weights=[70, 5, 5, 5, 5, 5, 3, 2])[0],
            "is_pep": is_pep,
            "timestamp": datetime.now() - timedelta(days=random.randint(0, 90))
        })

    df = pd.DataFrame(data)
    df.to_csv(f"{output_dir}/synthetic_transactions.csv", index=False)
    print(f"Generated {len(df)} transactions for AML testing in {output_dir}")

if __name__ == "__main__":
    generate_aml_test_data()
