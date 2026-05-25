import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_remittances(num_records=1500):
    print(f"Generating {num_records} cross-border remittance records...")
    
    countries = ['USA', 'UK', 'Germany', 'UAE', 'Canada', 'Saudi Arabia', 'Australia']
    corridors = [f"{c} -> Kenya" for c in countries]
    
    start_date = datetime.now() - timedelta(days=180)
    
    data = []
    for _ in range(num_records):
        sender_country = random.choice(countries)
        ts = start_date + timedelta(days=random.randint(0, 180), minutes=random.randint(0, 1440))
        
        # Seasonality: December spike
        amount_multiplier = 2.5 if ts.month == 12 else 1.0
        amount_usd = random.uniform(50, 3000) * amount_multiplier
        
        fee_percentage = random.uniform(0.01, 0.07)
        exchange_rate = 145.0 + random.uniform(-5, 10)
        
        data.append({
            'transfer_id': f"TX{random.randint(100000, 999999)}",
            'sender_country': sender_country,
            'receiver_country': 'Kenya',
            'amount_usd': round(amount_usd, 2),
            'transfer_fee_usd': round(amount_usd * fee_percentage, 2),
            'exchange_rate': round(exchange_rate, 2),
            'transfer_date': ts.date()
        })
        
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_remittances()
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/remittances_raw.csv', index=False)
    print("✅ Remittance data saved.")
