import pdfplumber

pdf_path = "Absa_Bank_Kenya(PIPELINE)/Absa-Group-Limited-Integrated-Report.pdf"
with pdfplumber.open(pdf_path) as pdf:
    # Scan for "Operating segments" or "Regional performance" in the full text to find the exact page
    print("Searching for Segmental/Geographical Reporting...")
    for i in range(len(pdf.pages)):
        text = pdf.pages[i].extract_text()
        if text and ("Segmental" in text or "Geographical" in text or "Kenya" in text):
            # Check for financial metrics presence on the same page
            if "Total assets" in text or "Net interest income" in text:
                print(f"Found potential financial table on page: {i+1}")
                # Print a bit more context
                print(text[:200])
                tables = pdf.pages[i].extract_tables()
                if tables:
                    print(f"Number of tables: {len(tables)}")
                    # If this looks like the right page, we stop searching
                    if "Kenya" in text:
                         print("Bingo! Kenya mentioned in financial context.")
                         # We'll print the tables for this page to confirm
                         for j, table in enumerate(tables):
                             print(f"Table {j+1} structure:")
                             for row in table[:5]:
                                 print(row)
                         # To avoid too much output, we limit the search results
                         # continue
