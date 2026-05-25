"""
Safaricom Plc Financial Results Data Warehouse

Extracts and analyzes Safaricom's quarterly financial results from
investor relations documents and stock exchange filings.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class FinancialResult:
    """Quarterly financial result."""
    reporting_period: str  # YYYY-Q format
    revenue: float
    ebitda: float
    net_profit: float
    earnings_per_share: float
    dividend_per_share: float
    report_date: datetime
    source_url: str


class IRWebScraper:
    """
    Scrape Safaricom Investor Relations website for financial data.
    
    Sources:
    - www.safaricom.co.ke/about-us/investor-relations
    - RNS (Regulatory News Service) announcements
    - NSE (Nairobi Securities Exchange) listings
    """
    
    BASE_URL = "https://www.safaricom.co.ke"
    IR_PATH = "/about-us/investor-relations"
    
    def __init__(self):
        """Initialize scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Data Engineering Pipeline)"
        })
    
    def scrape_ir_page(self) -> List[str]:
        """
        Scrape IR page for financial results links.
        
        Returns:
            list: URLs of financial documents
        """
        try:
            url = f"{self.BASE_URL}{self.IR_PATH}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find links to results announcements
            links = []
            for link in soup.find_all('a'):
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()
                
                if any(keyword in text for keyword in ['results', 'earnings', 'financial', 'annual', 'interim']):
                    full_url = href if href.startswith('http') else f"{self.BASE_URL}{href}"
                    links.append(full_url)
            
            logger.info(f"Found {len(links)} financial documents")
            return links
            
        except Exception as e:
            logger.error(f"Failed to scrape IR page: {str(e)}")
            return []
    
    def extract_from_announcement(self, url: str) -> Optional[FinancialResult]:
        """
        Extract financial figures from results announcement.
        
        Args:
            url: Document URL
            
        Returns:
            FinancialResult or None
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            content = response.text
            
            # Extract financial metrics using regex/parsing
            result = FinancialResult(
                reporting_period=self._extract_period(content),
                revenue=self._extract_value(content, 'revenue|total revenue'),
                ebitda=self._extract_value(content, 'ebitda'),
                net_profit=self._extract_value(content, 'profit|net profit|net income'),
                earnings_per_share=self._extract_value(content, 'eps|earnings per share'),
                dividend_per_share=self._extract_value(content, 'dividend|dps'),
                report_date=datetime.now(),
                source_url=url
            )
            
            logger.info(
                f"Extracted results for {result.reporting_period}: "
                f"Revenue KES {result.revenue:,.0f}M"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract from {url}: {str(e)}")
            return None
    
    @staticmethod
    def _extract_period(content: str) -> str:
        """Extract reporting period from content."""
        import re
        # Look for patterns like "Q1 2024" or "Year ended 31 December 2023"
        pattern = r'(?:Q[1-4]|Year ended|Six months ended)\s*(?:30|31)?\s*(?:June|December|March|September)?\s*(\d{4})'
        match = re.search(pattern, content, re.IGNORECASE)
        
        if match:
            return match.group(0)
        return "unknown"
    
    @staticmethod
    def _extract_value(content: str, pattern: str) -> float:
        """Extract numerical value from content."""
        import re
        # Look for currency values
        regex = f"{pattern}.*?([0-9,]+)\s*(?:million|m|billion|b)?"
        match = re.search(regex, content, re.IGNORECASE)
        
        if match:
            value_str = match.group(1).replace(',', '')
            return float(value_str)
        return 0.0


class SegmentAnalyzer:
    """
    Analyze Safaricom business segments.
    
    Segments:
    - Consumer (voice, SMS, data)
    - Business (enterprise services)
    - Wholesale (national roaming, international)
    - Digital Services (M-Pesa, fintech)
    """
    
    def __init__(self):
        """Initialize analyzer."""
        self.segments: Dict[str, Dict] = {}
    
    def add_segment_data(
        self,
        period: str,
        segment: str,
        revenue: float,
        subscribers: int,
        arpu: float
    ) -> None:
        """
        Add segment financial data.
        
        Args:
            period: Reporting period
            segment: Segment name
            revenue: Revenue in millions KES
            subscribers: Customer count
            arpu: Average Revenue Per User in KES
        """
        if period not in self.segments:
            self.segments[period] = {}
        
        self.segments[period][segment] = {
            "revenue": revenue,
            "subscribers": subscribers,
            "arpu": arpu,
            "revenue_contribution": 0,  # Calculated
            "subscriber_contribution": 0  # Calculated
        }
    
    def calculate_segment_metrics(self, period: str) -> Dict:
        """
        Calculate segment contribution metrics.
        
        Args:
            period: Reporting period
            
        Returns:
            dict: Segment metrics with contributions
        """
        if period not in self.segments:
            return {}
        
        segment_data = self.segments[period]
        total_revenue = sum(s.get("revenue", 0) for s in segment_data.values())
        total_subscribers = sum(s.get("subscribers", 0) for s in segment_data.values())
        
        for segment_name, segment_info in segment_data.items():
            segment_info["revenue_contribution"] = (
                segment_info["revenue"] / total_revenue * 100
                if total_revenue > 0 else 0
            )
            segment_info["subscriber_contribution"] = (
                segment_info["subscribers"] / total_subscribers * 100
                if total_subscribers > 0 else 0
            )
        
        return segment_data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scraper = IRWebScraper()
    print("Safaricom IR scraper module loaded")
