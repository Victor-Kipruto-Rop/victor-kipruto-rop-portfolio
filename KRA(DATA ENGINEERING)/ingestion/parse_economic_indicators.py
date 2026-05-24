import pdfplumber
import pandas as pd
import re
import os
from sqlalchemy import create_engine, text

def parse_economic_indicators():
    pdf_path = "KRA(DATA ENGINEERING)/Kenya-Leading-Economic-Indicators-February-2023.pdf"
    engine = create_engine('postgresql://kra_admin:kra_password@localhost:5438/kra_warehouse')

    data_points = []
    with pdfplumber.open(pdf_path) as pdf:
        # 1. Trade Totals (Page 5)
        text_p5 = pdf.pages[4].extract_text()
        m_exp = re.search(r"total exports.*?KSh ([\d\.,]+) billion", text_p5, re.IGNORECASE)
        m_imp = re.search(r"value of imports.*?KSh ([\d\.,]+) billion", text_p5, re.IGNORECASE)
        if m_exp: data_points.append({"indicator": "Total Exports", "value": float(m_exp.group(1)) * 1000, "unit": "M KES", "period": "2023-02-01"})
        if m_imp: data_points.append({"indicator": "Total Imports", "value": float(m_imp.group(1)) * 1000, "unit": "M KES", "period": "2023-02-01"})

        # 2. Inflation (Page 9 has Figure 1 text which is easier)
        text_p9 = pdf.pages[8].extract_text()
        # Look for Feb-23 and the value above it.
        # Figure 1: Inflation rates ... 9.23 (last value)
        m_infl = re.findall(r"(\d+\.\d+)", text_p9)
        if m_infl:
            data_points.append({"indicator": "Inflation Rate", "value": float(m_infl[-1]), "unit": "%", "period": "2023-02-01"})

        # 3. FX (Page 10)
        text_p10 = pdf.pages[9].extract_text()
        # "1 US Dollar............ 113.38 113.66 ... 125.45"
        m_usd = re.search(r"1 US Dollar.*?([\d\.,]+)$", text_p10, re.MULTILINE)
        if not m_usd:
            # Try to find the US Dollar line and get the last number
            lines = text_p10.split('\n')
            for line in lines:
                if "1 US Dollar" in line:
                    nums = re.findall(r"(\d+\.\d+)", line)
                    if nums:
                        data_points.append({"indicator": "USD/KES Rate", "value": float(nums[-1]), "unit": "KES", "period": "2023-02-01"})

    if data_points:
        df = pd.DataFrame(data_points)
        df.to_sql('macro_economic_indicators', engine, if_exists='replace', index=False)
        print(f"Successfully ingested {len(df)} indicators: {df['indicator'].tolist()}")
    else:
        print("Extraction failed.")

if __name__ == "__main__":
    parse_economic_indicators()
