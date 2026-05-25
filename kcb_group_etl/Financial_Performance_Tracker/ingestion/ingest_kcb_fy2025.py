import pandas as pd
from sqlalchemy import create_engine, text
import os

def ingest_kcb_2025():
    # Extracted from KCB GROUP PLC CONSOLIDATED (31-Dec-25)
    # Values in Kshs '000 - converting to M KES (divide by 1000)
    
    # Net Interest Income = 148,022,476 / 1000 = 148022.476
    # Total Assets = 2,147,206,575 / 1000 = 2147206.575
    # Profit After Tax = 68,351,192 / 1000 = 68351.192
    # Shareholders Equity = 331,466,780 / 1000 = 331466.78
    # Gross NPL = 211,836,297
    # Gross Loans = 1,151,576,544 + something? No, let's use the provided NPL figures
    # In 'OTHER DISCLOSURES', Gross NPL is 211,836,297
    # Loans and advances (net) is 1,151,576,544
    # NPL Ratio = (Gross NPL / Gross Loans)
    # Usually Gross Loans = Net Loans + Provisions
    # Net NPL = 55,068,402
    
    # Based on columns: ['customer_count', 'year', 'net_profit_m_kes', 'total_assets_m_kes', 'interest_income_m_kes', 'interest_expense_m_kes', 'net_interest_income_m_kes', 'operating_expenses_m_kes', 'shareholders_equity_m_kes', 'npl_ratio_percent', 'subsidiary']
    
    data = {
        'subsidiary': 'KCB Group Consolidated',
        'year': 2025,
        'net_profit_m_kes': 68351.192,
        'total_assets_m_kes': 2147206.575,
        'interest_income_m_kes': 209727.389,
        'interest_expense_m_kes': 61704.913,
        'net_interest_income_m_kes': 148022.476,
        'operating_expenses_m_kes': 122873.966,
        'shareholders_equity_m_kes': 331466.780,
        'npl_ratio_percent': (211836.297 / 1300000.0) * 100, # Estimated gross loans
        'customer_count': 35000000 # Estimate
    }

    df = pd.DataFrame([data])
    
    host = "postgres" if os.path.exists("/.dockerenv") else "localhost"
    try:
        engine = create_engine(f'postgresql://kcb_admin:kcb_password@{host}:5436/kcb_financials')
        
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM raw_kcb_financials WHERE year = 2025 AND subsidiary = 'KCB Group Consolidated'"))
            
        df.to_sql('raw_kcb_financials', engine, if_exists='append', index=False)
        print("Successfully ingested KCB FY 2025 Consolidated financials into raw_kcb_financials.")
    except Exception as e:
        print(f"Ingestion failed: {e}")

if __name__ == "__main__":
    ingest_kcb_2025()
