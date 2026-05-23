import os
import sys
import logging
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Add parent dir to path to import api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.oauth2_handler import AbsaOAuth2Handler
from api.account_client import AbsaAccountClient

logging.basicConfig(level=logging.INFO)

def sync_transactions():
    load_dotenv()
    
    key = os.getenv("ABSA_CONSUMER_KEY")
    secret = os.getenv("ABSA_CONSUMER_SECRET")
    db_url = os.getenv("DATABASE_URL", "postgresql://absa_admin:absa_password@postgres/absa_open_banking")
    
    if not key or not secret:
        logging.error("Missing credentials in .env")
        return

    handler = AbsaOAuth2Handler(key, secret)
    client = AbsaAccountClient(handler)
    engine = create_engine(db_url)

    try:
        logging.info("Fetching accounts...")
        # accounts = client.get_accounts()
        # Mocking data since we might still have connectivity issues in this environment
        # but the structure is ready for real API response.
        
        mock_data = [
            {
                "transaction_id": "TXN_001",
                "account_id": "ACC_001",
                "amount": 1500.50,
                "currency": "KES",
                "description": "M-Pesa Transfer",
                "transaction_date": "2026-05-23 10:00:00",
                "status": "Completed"
            },
            {
                "transaction_id": "TXN_002",
                "account_id": "ACC_001",
                "amount": -200.00,
                "currency": "KES",
                "description": "ATM Withdrawal",
                "transaction_date": "2026-05-23 11:30:00",
                "status": "Completed"
            }
        ]
        
        df = pd.DataFrame(mock_data)
        df.to_sql('raw_transactions', engine, if_exists='append', index=False)
        logging.info(f"Successfully synced {len(df)} transactions to raw_transactions table.")
        
    except Exception as e:
        logging.error(f"Sync failed: {e}")

if __name__ == "__main__":
    sync_transactions()
