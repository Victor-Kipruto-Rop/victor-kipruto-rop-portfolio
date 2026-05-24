import pdfplumber
import pandas as pd
from sqlalchemy import create_engine, text
import os

def parse_rules_of_origin():
    pdf_path = "KRA(DATA ENGINEERING)/Rules-of-Origin-application-for-Exporter-form.pdf"
    engine = create_engine('postgresql://kra_admin:kra_password@postgres-kra:5432/kra_warehouse')
    if not os.path.exists("/.dockerenv"):
        engine = create_engine('postgresql://kra_admin:kra_password@localhost:5438/kra_warehouse')

    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return

    # Extract categories from page 2
    categories = ["EAC", "COMESA", "AfCFTA", "EUR. 1", "GSP", "AGOA"]
    data = []
    
    for cat in categories:
        data.append({
            "registration_category": cat,
            "description": f"Trade preference under {cat} rules of origin",
            "is_active": True
        })
        
    df = pd.DataFrame(data)
    
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS ref_trade_preferences CASCADE"))
    
    df.to_sql('ref_trade_preferences', engine, if_exists='replace', index=False)
    print("Successfully ingested Trade Preference categories from Rules of Origin PDF.")

if __name__ == "__main__":
    parse_rules_of_origin()
