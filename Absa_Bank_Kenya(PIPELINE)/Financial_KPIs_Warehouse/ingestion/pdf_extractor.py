import pdfplumber
import pandas as pd
import os
import re

class AbsaPDFExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.data = []

    def extract_tables(self):
        """Extracts all tables from the PDF and returns them as a list of dataframes."""
        all_tables = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    all_tables.append(df)
        return all_tables

    def identify_financial_statement(self, df):
        """Identifies if a dataframe is likely an Income Statement or Balance Sheet."""
        text_blob = " ".join(df.iloc[:, 0].fillna("").astype(str).tolist()).lower()
        if "interest income" in text_blob or "profit before tax" in text_blob:
            return "income_statement"
        elif "total assets" in text_blob or "shareholders' equity" in text_blob:
            return "balance_sheet"
        return None

    def clean_financial_df(self, df):
        """Cleans a financial dataframe by removing empty rows and formatting numbers."""
        # Standardize columns: usually Column 0 is the metric name, others are years/quarters
        df = df.dropna(how='all', axis=0)
        df = df.dropna(how='all', axis=1)
        
        # Simple cleanup: remove special characters from numbers
        def clean_val(val):
            if isinstance(val, str):
                val = val.replace(",", "").replace("(", "-").replace(")", "").strip()
                if val == "-" or val == "":
                    return 0.0
                try:
                    return float(val)
                except ValueError:
                    return val
            return val

        for col in df.columns[1:]:
            df[col] = df[col].apply(clean_val)
        
        return df

    def run(self):
        tables = self.extract_tables()
        for df in tables:
            statement_type = self.identify_financial_statement(df)
            if statement_type:
                cleaned_df = self.clean_financial_df(df)
                # Here you would typically save to a staging area or database
                print(f"Extracted {statement_type}")
                print(cleaned_df.head())

if __name__ == "__main__":
    # Example usage (would be called by Airflow)
    # extractor = AbsaPDFExtractor("path/to/absa_report.pdf")
    # extractor.run()
    pass
