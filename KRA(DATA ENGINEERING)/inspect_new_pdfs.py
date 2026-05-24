import pdfplumber
import os

pdfs = [
    "KRA(DATA ENGINEERING)/202021-annual-revenue-performance-final.pdf",
    "KRA(DATA ENGINEERING)/Rules-of-Origin-application-for-Exporter-form.pdf"
]

for pdf_path in pdfs:
    print(f"\n--- Inspecting: {pdf_path} ---")
    if not os.path.exists(pdf_path):
        print("File not found.")
        continue
        
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total Pages: {len(pdf.pages)}")
        # Check first 5 pages for relevant tables/text
        for i in range(min(5, len(pdf.pages))):
            page = pdf.pages[i]
            text = page.extract_text()
            print(f"\n[Page {i+1} Snippet]:")
            print(text[:500] if text else "No text found.")
            
            tables = page.extract_tables()
            if tables:
                print(f"Found {len(tables)} tables on page {i+1}")
