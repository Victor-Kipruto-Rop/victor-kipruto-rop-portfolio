import pdfplumber
import pandas as pd

def extract_gdp_data():
    pdf_path = "KRA(DATA ENGINEERING)/2026-Economic-Survey.pdf"
    target_page = 69 # 0-indexed page 70
    
    print(f"Opening {pdf_path} and going to page {target_page+1}...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[target_page]
            tables = page.extract_tables()
            
            if not tables:
                print("No tables found on this page.")
                return
            
            table = tables[0]
            
            # The headers are something like: ['Industry', '2021', '2022', '2023', '2024+', '2025*']
            headers = [h.replace('+', '').replace('*', '').strip() if h else f'Col_{i}' for i, h in enumerate(table[0])]
            
            df = pd.DataFrame(table[1:], columns=headers)
            
            # Basic cleanup
            df = df.dropna(subset=[headers[0]]) 
            df = df[df[headers[0]] != '']
            
            print(f"\nExtracted DataFrame Head (Page {target_page+1}):")
            print(df.head(10))
            
            # You might want to save it as CSV
            csv_path = "KRA(DATA ENGINEERING)/ingestion/gdp_by_industry_current_prices.csv"
            df.to_csv(csv_path, index=False)
            print(f"\nSaved to {csv_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_gdp_data()
