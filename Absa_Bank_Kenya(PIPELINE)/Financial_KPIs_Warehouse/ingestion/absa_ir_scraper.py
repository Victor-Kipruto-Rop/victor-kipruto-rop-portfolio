import requests
from bs4 import BeautifulSoup
import os

class AbsaIRScraper:
    BASE_URL = "https://www.absa.co.ke/investor-relations/"
    
    def __init__(self, download_dir="data/absa_reports"):
        self.download_dir = download_dir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def get_report_links(self):
        """Scrapes the investor relations page for financial report links."""
        print(f"Scraping {self.BASE_URL}...")
        try:
            response = requests.get(self.BASE_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # This logic depends on the actual HTML structure of Absa's IR page
            links = []
            for a in soup.find_all('a', href=True):
                if ".pdf" in a['href'] and ("report" in a['href'].lower() or "financial" in a['href'].lower()):
                    links.append(a['href'])
            return list(set(links))
        except Exception as e:
            print(f"Error scraping Absa IR page: {e}")
            return []

    def download_reports(self, links):
        """Downloads the reports from the provided links."""
        for link in links:
            file_name = link.split("/")[-1]
            file_path = os.path.join(self.download_dir, file_name)
            if not os.path.exists(file_path):
                print(f"Downloading {file_name}...")
                try:
                    res = requests.get(link)
                    with open(file_path, 'wb') as f:
                        f.write(res.content)
                except Exception as e:
                    print(f"Failed to download {link}: {e}")
            else:
                print(f"{file_name} already exists.")

    def run(self):
        links = self.get_report_links()
        self.download_reports(links)

if __name__ == "__main__":
    scraper = AbsaIRScraper()
    scraper.run()
