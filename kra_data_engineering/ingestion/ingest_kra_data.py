import pandas as pd
from sqlalchemy import create_engine, text
import os
import numpy as np

def ingest_revenue_data(engine):
    # Mock data based on 2020-21 and 2024-25 reports
    print("Ingesting Revenue Data...")
    tax_heads = ['PAYE', 'VAT', 'Customs', 'Excise', 'Corporation Tax']
    data = []
    
    # 2020-2021 Data
    for month in range(1, 13):
        for th in tax_heads:
            target = np.random.uniform(10000, 50000)
            actual = target * np.random.uniform(0.85, 1.15)
            data.append({
                'tax_head': th,
                'year': 2021,
                'month': month,
                'actual_revenue_m_kes': round(actual, 2),
                'target_revenue_m_kes': round(target, 2),
                'reported_date': f'2021-{month:02d}-28'
            })
            
    # 2024-2025 Data
    for month in range(1, 13):
        for th in tax_heads:
            target = np.random.uniform(15000, 60000)
            actual = target * np.random.uniform(0.9, 1.1)
            data.append({
                'tax_head': th,
                'year': 2024,
                'month': month,
                'actual_revenue_m_kes': round(actual, 2),
                'target_revenue_m_kes': round(target, 2),
                'reported_date': f'2024-{month:02d}-28'
            })
            
    df = pd.DataFrame(data)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE raw_kra_revenue CASCADE;"))
    df.to_sql('raw_kra_revenue', engine, if_exists='append', index=False)
    print("Successfully ingested Revenue Data into raw_kra_revenue.")

def ingest_customs_declarations(engine):
    print("Ingesting Customs Declarations Data (Rules of Origin & Trade Data)...")
    hs_codes = ['090111', '060311', '271012', '870323'] # Coffee, Flowers, Fuel, Cars
    origins = ['Uganda', 'Tanzania', 'China', 'Japan']
    destinations = ['Kenya', 'Kenya', 'Kenya', 'Kenya']
    
    data = []
    for i in range(100):
        data.append({
            'declaration_id': f'DEC{i:05d}',
            'date': f'2024-{np.random.randint(1, 13):02d}-{np.random.randint(1, 28):02d}',
            'hs_code': np.random.choice(hs_codes),
            'origin_country': np.random.choice(origins),
            'destination_country': np.random.choice(destinations),
            'declared_value_kes': np.random.uniform(100000, 5000000),
            'duty_paid_kes': np.random.uniform(10000, 500000),
            'has_rules_of_origin_cert': np.random.choice([True, False])
        })
        
    df = pd.DataFrame(data)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS raw_customs_declarations CASCADE;"))
    df.to_sql('raw_customs_declarations', engine, if_exists='append', index=False)
    print("Successfully ingested Customs Declarations into raw_customs_declarations.")

if __name__ == '__main__':
    host = "postgres-kra" if os.path.exists("/.dockerenv") else "localhost"
    try:
        engine = create_engine(f'postgresql://kra_admin:kra_password@{host}:5438/kra_warehouse')
        ingest_revenue_data(engine)
        ingest_customs_declarations(engine)
    except Exception as e:
        print(f"Connection failed: {e}")
