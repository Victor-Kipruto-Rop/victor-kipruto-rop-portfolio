import pdfplumber

pdf_path = "KRA(DATA ENGINEERING)/202021-annual-revenue-performance-final.pdf"
with pdfplumber.open(pdf_path) as pdf:
    # Checking pages 8 to 15 which usually contain the meat of the performance data
    for i in range(7, 15):
        page = pdf.pages[i]
        print(f"\n--- Page {i+1} ---")
        print(page.extract_text())
        tables = page.extract_tables()
        if tables:
            print(f"Found {len(tables)} tables on page {i+1}")
            for j, table in enumerate(tables):
                print(f"Table {j+1}:")
                for row in table[:10]: # Print first 10 rows
                    print(row)
