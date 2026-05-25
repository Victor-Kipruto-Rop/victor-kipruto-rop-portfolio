import pandas as pd
import os
from datetime import datetime

class NSEParser:
    """
    Parses NSE filings (CSV/Excel format) for Absa Bank Kenya.
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self):
        print(f"Parsing NSE filing: {self.file_path}")
        if not os.path.exists(self.file_path):
            print(f"File not found: {self.file_path}")
            return pd.DataFrame()

        if self.file_path.endswith('.csv'):
            df = pd.read_csv(self.file_path)
        elif self.file_path.endswith('.xlsx'):
            df = pd.read_excel(self.file_path)
        else:
            raise ValueError("Unsupported file format. Use CSV or XLSX.")
        
        # Mapping NSE standard labels to our warehouse schema
        mapping = {
            'Profit After Tax': 'Net Income',
            'Interest Income': 'Net Interest Income',
            'Total Assets': 'Average Earning Assets',
            'Total Shareholders Equity': 'Average Shareholders Equity',
            'Operating Expenses': 'Operating Expenses',
            'Total Operating Income': 'Total Operating Income',
            'Gross Non-Performing Loans': 'Non-Performing Loans',
            'Gross Loans and Advances': 'Gross Loans',
            'Total Regulatory Capital': 'Total Capital',
            'Total Risk Weighted Assets': 'Risk-Weighted Assets'
        }
        
        # Expecting columns: 'Label', 'Period', 'Value'
        if 'Label' in df.columns and 'Period' in df.columns and 'Value' in df.columns:
            df['metric_name'] = df['Label'].map(mapping)
            df = df.dropna(subset=['metric_name'])
            df['extracted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return df[['metric_name', 'Period', 'Value', 'extracted_at']].rename(columns={'Period': 'period', 'Value': 'value'})
        
        print("Required columns (Label, Period, Value) not found in filing.")
        return pd.DataFrame()

if __name__ == "__main__":
    # Integration test with dummy CSV
    dummy_path = "test_filing.csv"
    pd.DataFrame({
        'Label': ['Profit After Tax', 'Total Assets'],
        'Period': ['2024-Q4', '2024-Q4'],
        'Value': [12000000, 450000000]
    }).to_csv(dummy_path, index=False)
    
    parser = NSEParser(dummy_path)
    print(parser.parse())
    os.remove(dummy_path)
