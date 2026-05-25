import pdfplumber

pdf_path = "Absa_Bank_Kenya(PIPELINE)/Absa-Group-Limited-Integrated-Report.pdf"
with pdfplumber.open(pdf_path) as pdf:
    # Page 25
    print("\n--- Page 25 Content ---")
    print(pdf.pages[24].extract_text())
    tables = pdf.pages[24].extract_tables()
    if tables:
        for j, table in enumerate(tables):
            print(f"Table {j+1}:")
            for row in table[:10]:
                print(row)

    # Page 59
    print("\n--- Page 59 Content ---")
    print(pdf.pages[58].extract_text())
    tables = pdf.pages[58].extract_tables()
    if tables:
        for j, table in enumerate(tables):
            print(f"Table {j+1}:")
            for row in table[:10]:
                print(row)
