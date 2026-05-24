import pdfplumber
import os

pdf_path = "KRA(DATA ENGINEERING)/Kenya-Leading-Economic-Indicators-February-2023.pdf"

if not os.path.exists(pdf_path):
    print(f"Error: PDF not found at {pdf_path}")
else:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total Pages: {len(pdf.pages)}")
        # Inspect first 10 pages for indices or specific tables
        for i in range(min(10, len(pdf.pages))):
            page = pdf.pages[i]
            text = page.extract_text()
            print(f"\n[Page {i+1} Snippet]:")
            print(text[:500] if text else "No text found.")
            
            tables = page.extract_tables()
            if tables:
                print(f"Found {len(tables)} tables on page {i+1}")
