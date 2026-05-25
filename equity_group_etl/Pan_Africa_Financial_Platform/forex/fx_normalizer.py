import pandas as pd
import requests

class FXNormalizer:
    """
    Simulates currency normalization to USD and KES using mock exchange rates
    (to avoid live API dependency in test/dev environment).
    """
    def __init__(self):
        # Mock rates relative to 1 USD
        self.rates_to_usd = {
            "KES": 130.0,
            "UGX": 3800.0,
            "TZS": 2600.0,
            "CDF": 2800.0,
            "RWF": 1280.0,
            "SSP": 1100.0,
            "ETB": 57.0,
            "USD": 1.0
        }

    def normalize(self, amount: float, currency: str) -> dict:
        rate = self.rates_to_usd.get(currency)
        if not rate:
            return {"usd": 0, "kes": 0}
        
        amount_usd = amount / rate
        amount_kes = amount_usd * self.rates_to_usd["KES"]
        
        return {
            "usd": round(amount_usd, 2),
            "kes": round(amount_kes, 2)
        }

if __name__ == "__main__":
    normalizer = FXNormalizer()
    print(normalizer.normalize(15000000000, "KES"))
