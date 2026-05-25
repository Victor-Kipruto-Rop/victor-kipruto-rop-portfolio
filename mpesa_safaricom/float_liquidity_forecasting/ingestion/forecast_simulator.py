import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_historical_float(num_days=365):
    print(f"Generating {num_days} days of historical float data...")
    
    start_date = datetime.now() - timedelta(days=num_days)
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    
    # Simulating a clear weekly pattern + seasonality
    data = []
    base_demand = 50000
    
    for d in dates:
        # Weekend spike
        weekday_multiplier = 1.4 if d.weekday() >= 5 else 1.0
        # Month end spike (payday)
        month_end_multiplier = 1.8 if d.day >= 25 or d.day <= 5 else 1.0
        # Random noise
        noise = np.random.normal(0, 0.05)
        
        float_demand = base_demand * weekday_multiplier * month_end_multiplier * (1 + noise)
        
        data.append({
            'date': d.date(),
            'float_demand_kes': round(float_demand, 2),
            'day_of_week': d.strftime('%A'),
            'is_weekend': d.weekday() >= 5
        })
        
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_historical_float()
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/historical_float.csv', index=False)
    print("✅ Historical float data saved.")
