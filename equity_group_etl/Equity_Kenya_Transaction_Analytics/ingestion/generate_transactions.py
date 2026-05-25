import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

def generate_equity_kenya_transactions():
    print("Generating Equity Kenya Transaction Data...")
    
    np.random.seed(42)
    num_transactions = 5000
    
    channels = ['EazzyPay', 'Equitel', 'ATM', 'Agency Banking', 'Equity Mobile', 'Visa Card']
    categories = ['Retail', 'Utility Bill', 'Peer-to-Peer', 'Merchant Payment', 'Withdrawal', 'Deposit']
    counties = ['Nairobi', 'Mombasa', 'Kiambu', 'Nakuru', 'Uasin Gishu', 'Kisumu', 'Kajiado']
    
    start_date = datetime(2025, 1, 1)
    
    data = []
    for i in range(num_transactions):
        txn_date = start_date + timedelta(days=np.random.randint(0, 145), 
                                          hours=np.random.randint(0, 24),
                                          minutes=np.random.randint(0, 60))
        
        channel = np.random.choice(channels)
        category = np.random.choice(categories)
        
        if category == 'Retail':
            amount = np.random.uniform(500, 15000)
        elif category == 'Utility Bill':
            amount = np.random.uniform(1000, 25000)
        elif category == 'Peer-to-Peer':
            amount = np.random.uniform(100, 100000)
        else:
            amount = np.random.uniform(1000, 250000)
            
        data.append({
            'transaction_id': f'EQK{i:06d}',
            'timestamp': txn_date,
            'channel': channel,
            'category': category,
            'amount_kes': round(amount, 2),
            'county': np.random.choice(counties, p=[0.4, 0.1, 0.15, 0.1, 0.1, 0.1, 0.05]),
            'is_fraudulent': np.random.choice([True, False], p=[0.005, 0.995])
        })
        
    df = pd.DataFrame(data)
    
    # Save to ingestion CSV
    output_dir = "Equity_Group(PIPELINE_ETL)/Equity_Kenya_Transaction_Analytics/ingestion"
    df.to_csv(f"{output_dir}/equity_kenya_transactions_raw.csv", index=False)
    
    # Pre-generate snapshots for dashboard
    snapshot_dir = "Equity_Group(PIPELINE_ETL)/Equity_Kenya_Transaction_Analytics/dashboards/snapshots"
    os.makedirs(snapshot_dir, exist_ok=True)
    
    # Mart 1: Channel Performance
    mart_channel = df.groupby('channel').agg(
        total_transactions=('transaction_id', 'count'),
        total_volume_kes=('amount_kes', 'sum'),
        avg_transaction_value=('amount_kes', 'mean')
    ).reset_index()
    mart_channel.to_csv(f"{snapshot_dir}/mart_kenya_channel_performance.csv", index=False)
    
    # Mart 2: County Activity
    mart_county = df.groupby('county').agg(
        transaction_count=('transaction_id', 'count'),
        volume_kes=('amount_kes', 'sum')
    ).reset_index()
    mart_county.to_csv(f"{snapshot_dir}/mart_kenya_county_activity.csv", index=False)
    
    # Mart 3: Daily Trends
    df['date'] = df['timestamp'].dt.date
    mart_trends = df.groupby('date').agg(
        transaction_count=('transaction_id', 'count'),
        total_volume=('amount_kes', 'sum')
    ).reset_index()
    mart_trends.to_csv(f"{snapshot_dir}/mart_kenya_transaction_trends.csv", index=False)
    
    print(f"Successfully generated 5,000 Kenya transactions and created snapshots.")
    
    # Ingest into Postgres
    host = "postgres-equity" if os.path.exists("/.dockerenv") else "localhost"
    try:
        engine = create_engine(f'postgresql://equity_admin:equity_password@{host}:5441/equity_warehouse')
        df.to_sql('raw_equity_kenya_transactions', engine, if_exists='replace', index=False)
        print("Successfully ingested into Postgres.")
    except Exception as e:
        print(f"DB Ingestion skipped (Host unreachable). Portable CSV snapshots ready.")

if __name__ == "__main__":
    generate_equity_kenya_transactions()
