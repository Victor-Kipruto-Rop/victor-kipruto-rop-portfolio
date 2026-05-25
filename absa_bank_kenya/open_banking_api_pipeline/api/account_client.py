import requests
import urllib3
from .oauth2_handler import AbsaOAuth2Handler

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AbsaAccountClient:
    # Based on user verified port, adjusting base URL
    BASE_URL = "https://www.api.absa.africa:9443/open-banking/v1"

    def __init__(self, oauth_handler: AbsaOAuth2Handler):
        self.oauth_handler = oauth_handler

    def get_accounts(self):
        """Fetches all accounts for the authorized user."""
        token = self.oauth_handler.get_token()
        headers = {
            "Authorization": f"Bearer {token}", 
            "Accept": "application/json"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/accounts", 
            headers=headers, 
            verify=False, 
            timeout=15
        )
        response.raise_for_status()
        return response.json()

    def get_transactions(self, account_id):
        """Fetches transactions for a specific account."""
        token = self.oauth_handler.get_token()
        headers = {
            "Authorization": f"Bearer {token}", 
            "Accept": "application/json"
        }
        
        response = requests.get(
            f"{self.BASE_URL}/accounts/{account_id}/transactions", 
            headers=headers, 
            verify=False, 
            timeout=15
        )
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    pass
