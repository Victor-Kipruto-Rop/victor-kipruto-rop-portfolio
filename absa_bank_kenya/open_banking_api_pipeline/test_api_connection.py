import os
import sys
from dotenv import load_dotenv

# Add parent dir to path to import local api modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api.oauth2_handler import AbsaOAuth2Handler
    from api.account_client import AbsaAccountClient
except ImportError:
    print("Error: Modules not found. Run from Open_Banking_API_Pipeline directory.")
    sys.exit(1)

def test_connection():
    # Load from parent folder .env if it exists
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    
    key = os.getenv("ABSA_CONSUMER_KEY")
    secret = os.getenv("ABSA_CONSUMER_SECRET")
    
    if not key or not secret:
        print("❌ Error: ABSA_CONSUMER_KEY or ABSA_CONSUMER_SECRET not found in environment.")
        print("Please create a .env file in the Absa_Bank_Kenya(PIPELINE) directory.")
        return

    print("🚀 Initializing Absa API Connection Test...")
    oauth = AbsaOAuth2Handler(key, secret)
    
    token = oauth.get_token()
    if token:
        print("✅ Success: OAuth2 Token retrieved.")
        
        client = AbsaAccountClient(oauth)
        try:
            print("📡 Fetching account list...")
            accounts = client.get_accounts()
            print(f"✅ Success: Retrieved {len(accounts.get('Data', {}).get('Account', []))} accounts from Playpen.")
            print("\nConnection verification complete!")
        except Exception as e:
            print(f"❌ Account fetch failed: {e}")
            print("Note: The Playpen sometimes requires specific consent IDs or may have intermittent downtime.")
    else:
        print("❌ OAuth2 Token retrieval failed. Check your credentials.")

if __name__ == "__main__":
    test_connection()
