import pandas as pd

class ContrabandScorer:
    """Calculates risk scores for shipments based on origin, commodity, and historical compliance."""
    
    def __init__(self, declarations_df, country_risk_df):
        self.df = declarations_df
        self.country_risk = country_risk_df

    def calculate_scores(self):
        """Scores shipments from 0-100 based on risk factors."""
        if self.df.empty: return pd.DataFrame()
        
        # Merge with country risk scores
        merged = self.df.merge(self.country_risk, left_on='origin_country', right_on='country_name', how='left')
        
        # Weights
        # 40% Country Risk, 40% Commodity Sensitivity, 20% Valuation Anomaly
        merged['calculated_risk'] = (
            merged['composite_risk_score'] * 0.4 + 
            merged['risk_score'] * 0.4 + # existing commodity risk
            np.random.uniform(0, 20, len(merged)) # random noise for demo
        )
        
        return merged.clip(upper=100)

import numpy as np
if __name__ == "__main__":
    print("Contraband scoring logic initialized.")
