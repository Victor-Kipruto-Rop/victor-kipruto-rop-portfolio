import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class VintageAnalyzer:
    """Performs vintage analysis on loan data."""
    
    def __init__(self, df):
        self.df = df
        
    def calculate_default_rates(self):
        """Calculates default rates per cohort and month offset."""
        if self.df.empty:
            return pd.DataFrame()
            
        # Ensure column types
        self.df['amount_disbursed_m_kes'] = pd.to_numeric(self.df['amount_disbursed_m_kes'])
        self.df['npl_amount_m_kes'] = pd.to_numeric(self.df['npl_amount_m_kes'])
        
        # Calculate default rate
        self.df['default_rate_percent'] = (self.df['npl_amount_m_kes'] / self.df['amount_disbursed_m_kes']) * 100
        
        return self.df

    def get_vintage_matrix(self):
        """Returns a pivot table suitable for heatmap visualization."""
        df = self.calculate_default_rates()
        if df.empty:
            return pd.DataFrame()
            
        matrix = df.pivot(index='cohort_month', columns='month_offset', values='default_rate_percent')
        return matrix

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("KCB M-Pesa Vintage Analyzer module initialized")
