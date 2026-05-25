import pandas as pd
import numpy as np
import random
from faker import Faker
import os

fake = Faker()

def generate_merchants(num_merchants=300):
    print(f"Generating data for {num_merchants} M-Pesa merchants...")
    
    categories = ['Retail', 'Pharmacy', 'Petrol Station', 'Restaurant', 'Hardware', 'Electronics']
    counties = ['Nairobi', 'Mombasa', 'Kiambu', 'Nakuru', 'Uasin Gishu', 'Kisumu', 'Kajiado']
    
    data = []
    for _ in range(num_merchants):
        merchant_id = f"MID{random.randint(10000, 99999)}"
        name = fake.company()
        category = random.choice(categories)
        county = random.choice(counties)
        
        # Transaction activity
        daily_txns = random.randint(5, 500)
        avg_ticket = random.uniform(200, 50000)
        churn_score = random.uniform(0, 1) # 0 to 1 risk
        
        data.append({
            'merchant_id': merchant_id,
            'name': name,
            'category': category,
            'county': county,
            'daily_transactions': daily_txns,
            'avg_ticket_size_kes': round(avg_ticket, 2),
            'churn_risk_score': round(churn_score, 2),
            'monthly_volume_kes': round(daily_txns * 30 * avg_ticket, 2)
        })
        
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_merchants()
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/merchants_raw.csv', index=False)
    print("✅ Merchant data saved.")
