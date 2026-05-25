import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os
from sqlalchemy import create_engine

fake = Faker()

def generate_agents(num_agents=200):
    print(f"Generating data for {num_agents} M-Pesa agents...")
    counties = ['Nairobi', 'Mombasa', 'Kiambu', 'Nakuru', 'Uasin Gishu', 'Kisumu', 'Kajiado']
    
    data = []
    for i in range(num_agents):
        agent_id = f"AG{1000 + i}"
        county = random.choice(counties)
        # Random location within county (simulated)
        lat = random.uniform(-4.5, 4.5)
        lon = random.uniform(34.0, 41.0)
        
        float_balance = random.uniform(500, 500000)
        transactions_today = random.randint(0, 50)
        last_restock = datetime.now() - timedelta(days=random.randint(0, 5), hours=random.randint(0, 23))
        
        data.append({
            'agent_id': agent_id,
            'county': county,
            'latitude': lat,
            'longitude': lon,
            'float_balance': round(float_balance, 2),
            'txns_today': transactions_today,
            'last_restock_at': last_restock,
            'is_active': random.choices([True, False], weights=[0.95, 0.05])[0]
        })
        
    return pd.DataFrame(data)

def ingest_agents(df):
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/agents_raw.csv', index=False)
    
    # DB Ingestion Logic (standard across portfolio)
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = '5439' # External port
    engine = create_engine(f'postgresql://mpesa_admin:mpesa_password@{db_host}:{db_port}/mpesa_warehouse')
    try:
        df.to_sql('raw_agents', engine, if_exists='replace', index=False)
        print("✅ Agents ingested to DB.")
    except:
        print("⚠️ DB ingestion failed. Using CSV snapshots.")

if __name__ == "__main__":
    df = generate_agents()
    ingest_agents(df)
