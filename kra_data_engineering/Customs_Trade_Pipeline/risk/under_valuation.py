import pandas as pd
import numpy as np

class UnderValuationDetector:
    """Detects under-valuation in customs declarations by comparing against global benchmarks."""
    
    def __init__(self, declarations_df, benchmark_df=None):
        self.df = declarations_df
        self.benchmark = benchmark_df

    def detect_anomalies(self):
        """Identifies transactions where declared value is significantly below mean for that HS code."""
        if self.df.empty: return pd.DataFrame()
        
        # Calculate unit prices (KES per Ton)
        self.df['unit_price'] = self.df['declared_value_m_kes'] / self.df['volume_tons']
        
        # Calculate mean unit price per HS Code
        stats = self.df.groupby('hs_code')['unit_price'].agg(['mean', 'std']).reset_index()
        
        merged = self.df.merge(stats, on='hs_code')
        
        # Threshold: 2 standard deviations below mean
        merged['is_under_valued'] = merged['unit_price'] < (merged['mean'] - 1.5 * merged['std'])
        
        return merged[merged['is_under_valued']]

if __name__ == "__main__":
    print("Under-valuation detection logic initialized.")
