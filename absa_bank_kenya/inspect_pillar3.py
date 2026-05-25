import pdfplumber

pdf_path = "Absa_Bank_Kenya(PIPELINE)/Absa-Group-Pillar-3-disclosure-as-at-31-December-2025.pdf"
with pdfplumber.open(pdf_path) as pdf:
    print(f"Scanning {pdf_path} for technical tables...")
    # Pillar 3 usually has tables with many columns
    for i in range(len(pdf.pages)):
        text = pdf.pages[i].extract_text()
        if text and "Kenya" in text and ("Credit risk" in text or "Capital" in text or "Stage 3" in text):
            print(f"Found potential risk table on page: {i+1}")
            print(text[:300])
            tables = pdf.pages[i].extract_tables()
            if tables:
                print(f"Tables found: {len(tables)}")
                # Show first table structure
                for row in tables[0][:10]:
                    print(row)
                # break # Just find the first good one for now
