import pytest
import pandas as pd
from ingestion.pdf_extractor import AbsaPDFExtractor

def test_identify_financial_statement_income():
    extractor = AbsaPDFExtractor("mock.pdf")
    df = pd.DataFrame({"Metric": ["Interest Income", "Total Costs"]})
    assert extractor.identify_financial_statement(df) == "income_statement"

def test_identify_financial_statement_balance():
    extractor = AbsaPDFExtractor("mock.pdf")
    df = pd.DataFrame({"Metric": ["Total Assets", "Loans"]})
    assert extractor.identify_financial_statement(df) == "balance_sheet"

def test_clean_financial_df():
    extractor = AbsaPDFExtractor("mock.pdf")
    data = {
        "Metric": ["NII", "ROE"],
        "2023": ["1,000", "(200)"],
        "2022": ["-", ""]
    }
    df = pd.DataFrame(data)
    cleaned = extractor.clean_financial_df(df)
    
    assert cleaned["2023"].iloc[0] == 1000.0
    assert cleaned["2023"].iloc[1] == -200.0
    assert cleaned["2022"].iloc[0] == 0.0
    assert cleaned["2022"].iloc[1] == 0.0
