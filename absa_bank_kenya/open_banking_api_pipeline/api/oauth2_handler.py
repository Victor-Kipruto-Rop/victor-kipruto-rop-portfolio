import requests
import os
import base64
from datetime import datetime, timedelta
import urllib3

# Suppress insecure request warnings if we use verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AbsaOAuth2Handler:
    """
    Handles OAuth2 authentication using verified endpoint and credentials.
    """
    def __init__(self, consumer_key, consumer_secret, token_url="https://www.api.absa.africa:9443/oauth2/token"):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token_url = token_url
        self.access_token = None
        self.expires_at = None

    def get_token(self):
        """Fetches a new access token using verified curl parameters."""
        if self.access_token and self.expires_at > datetime.now():
            return self.access_token

        print(f"Fetching new OAuth2 token from {self.token_url}...")
        
        # Prepare Basic Auth header
        auth_str = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        payload = {
            'grant_type': 'client_credentials'
        }
        
        try:
            # Using verify=False to match curl -k behavior
            response = requests.post(
                self.token_url, 
                data=payload, 
                headers=headers, 
                verify=False, 
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            self.access_token = data['access_token']
            # Default to 1 hour if expires_in is missing
            expires_in = data.get('expires_in', 3600)
            self.expires_at = datetime.now() + timedelta(seconds=int(expires_in) - 60)
            return self.access_token
        except Exception as e:
            print(f"Failed to fetch OAuth2 token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response Status: {e.response.status_code}")
                print(f"Response Body: {e.response.text}")
            return None

if __name__ == "__main__":
    pass
