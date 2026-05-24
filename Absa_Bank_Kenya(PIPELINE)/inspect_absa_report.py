import pdfplumber
import os

pdf_path = "Absa_Bank_Kenya(PIPELINE)/Absa-Group-Limited-Integrated-Report.pdf"

if not os.path.exists(pdf_path):
    print(f"Error: PDF not found at {pdf_path}")
else:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total Pages: {len(pdf.pages)}")
        # Scan for keywords in the first 50 pages to find geographical or segment reports
        for i in range(min(100, len(pdf.pages))):
            page = pdf.pages[i]
            text = page.extract_text()
            if text:
                if "Kenya" in text and ("Profit" in text or "Revenue" in text):
                    print(f"Potential Kenya data found on page: {i+1}")
                if "Segmental" in text or "Geographical" in text:
                    print(f"Potential segment/geographical report found on page: {i+1}")
