import pdfplumber
import os

pdf_path = "/opt/airflow/projects/financials/ingestion/kcb-group-plc-fy-2025-audited-financial-statements-1773238527.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total Pages: {len(pdf.pages)}")
    first_page = pdf.pages[0]
    print("--- Page 1 Content Snippet ---")
    print(first_page.extract_text()[:500] if first_page.extract_text() else "No text found")
