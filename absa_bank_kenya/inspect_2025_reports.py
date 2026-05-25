import pdfplumber
import os

pdfs = [
    "Absa_Bank_Kenya(PIPELINE)/Absa-Group-Pillar-3-disclosure-as-at-31-December-2025.pdf",
    "Absa_Bank_Kenya(PIPELINE)/2025-integrated-annual-report.pdf"
]

for pdf_path in pdfs:
    print(f"\n--- Inspecting: {pdf_path} ---")
    if not os.path.exists(pdf_path):
        print("File not found.")
        continue
        
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total Pages: {len(pdf.pages)}")
        # Check first 30 pages
        for i in range(min(30, len(pdf.pages))):
            page = pdf.pages[i]
            text = page.extract_text()
            if text:
                if "Kenya" in text and ("NPL" in text or "Ratio" in text or "Profit" in text or "Asset" in text):
                    print(f"Potential Kenya data found on page: {i+1}")
                    print(f"Snippet: {text[:200].replace('\n', ' ')}")
