import requests
import urllib3

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PaymentInitiationClient:
    """
    Handles payment initiation requests via the Absa Open Banking API.
    """
    def __init__(self, oauth_handler):
        self.oauth_handler = oauth_handler
        self.base_url = "https://www.api.absa.africa:9443/open-banking/v1/payments"

    def initiate_payment(self, payment_details):
        token = self.oauth_handler.get_token()
        headers = {
            "Authorization": f"Bearer {token}", 
            "Content-Type": "application/json"
        }
        response = requests.post(
            self.base_url, 
            json=payment_details, 
            headers=headers, 
            verify=False, 
            timeout=15
        )
        response.raise_for_status()
        return response.json()
