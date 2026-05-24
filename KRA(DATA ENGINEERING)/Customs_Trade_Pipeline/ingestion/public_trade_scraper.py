from requests_html import HTMLSession
import pandas as pd
import os
import logging
import time

class PublicTradeScraper:
    """
    Scrapes public trade data from the ITC TradeMap Beta portal.
    URL: https://beta.trademap.org/Country_SelProduct_TS.aspx?nvpm=1|404||||TOTAL|||2|1|1|1|2|1|1|1|1|1
    """
    
    def __init__(self):
        self.session = HTMLSession()
        self.url = "https://beta.trademap.org/Country_SelProduct_TS.aspx?nvpm=1|404||||TOTAL|||2|1|1|1|2|1|1|1|1|1"
        
    def scrape_kenya_indicators(self):
        """
        Uses Requests-HTML to render JavaScript and extract the trade indicators table.
        """
        try:
            print(f"Connecting to ITC TradeMap Beta: {self.url}")
            r = self.session.get(self.url)
            
            # Rendering JS (this downloads Chromium in the background if not present)
            # We use a sleep to ensure the table data loads after JS execution
            print("Rendering JavaScript dynamic content...")
            r.html.render(sleep=5, timeout=30)
            
            # Look for the data table
            # On the beta site, the table usually has a specific ID or class
            table = r.html.find('#ctl00_PageContent_GridView_SelectedCountry', first=True)
            
            if not table:
                # Try generic table search if specific ID fails
                table = r.html.find('table', first=True)
                
            if not table:
                print("Could not find the trade data table on the page.")
                return pd.DataFrame()
                
            # Parse rows
            rows = table.find('tr')
            data = []
            for row in rows[1:]: # Skip header
                cols = row.find('td')
                if len(cols) >= 5:
                    data.append({
                        "hs_code": cols[0].text.strip(),
                        "commodity": cols[1].text.strip(),
                        "value_2023": cols[2].text.strip().replace(',', ''),
                        "growth_rate": cols[3].text.strip()
                    })
            
            df = pd.DataFrame(data)
            print(f"Scraped {len(df)} rows from TradeMap Beta.")
            return df
            
        except Exception as e:
            print(f"Scraping failed: {e}")
            return pd.DataFrame()

    def run_ingestion(self, project_dir=None):
        if project_dir is None:
            if os.path.exists("/opt/airflow/projects/kra"):
                project_dir = "/opt/airflow/projects/kra/Customs_Trade_Pipeline"
            else:
                project_dir = "KRA(DATA ENGINEERING)/Customs_Trade_Pipeline"

        df = self.scrape_kenya_indicators()
        if not df.empty:
            output_path = os.path.join(project_dir, "ingestion/scraped_itc_benchmarks.csv")
            df.to_csv(output_path, index=False)
            print(f"Saved scraped data to {output_path}")
        else:
            print("No data scraped. Ensure internet access and check CSS selectors.")

if __name__ == "__main__":
    scraper = PublicTradeScraper()
    scraper.run_ingestion()
