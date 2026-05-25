"""
KRA Tax Revenue Analytics - Press Release Parser and Data Extractor

Extracts structured tax revenue data from KRA monthly and annual
press releases using NLP and regex patterns.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import PyPDF2  # For PDF parsing

logger = logging.getLogger(__name__)


class TaxHead(Enum):
    """KRA tax head categories."""
    INCOME_TAX = "income_tax"
    VAT = "vat"
    EXCISE = "excise"
    CUSTOMS = "customs_duty"
    CORPORATION_TAX = "corporation_tax"
    WITHHOLDING_TAX = "withholding_tax"
    STAMP_DUTY = "stamp_duty"
    OTHER = "other"


@dataclass
class TaxRevenueRecord:
    """Tax revenue record from press release."""
    report_date: datetime
    tax_head: TaxHead
    collection_amount: float
    currency: str = "KES"
    year_to_date: float = None
    previous_year_comparison: float = None
    target_amount: float = None
    achievement_percent: float = None
    source_url: str = None


class PressReleaseParser:
    """
    Parse KRA press releases to extract revenue figures.
    
    Pattern examples:
    - "Total tax revenue for November 2023: KES 176.5 billion"
    - "Income tax collections: KES 85.2 billion (up from 78.3 billion in Oct)"
    """
    
    # Regex patterns for revenue extraction
    PATTERNS = {
        "revenue_statement": r"([A-Za-z\s]+):\s*(?:KES|Kes|kes)?\s*([\d,]+\.?\d*)\s*(?:billion|million|thousand|bn|m|k)?",
        "date": r"([A-Za-z]+)\s+(\d{4})",
        "year_to_date": r"year[\s-]?to[\s-]?date.*?(?:KES|Kes)?\s*([\d,]+\.?\d*)\s*(?:billion|million)?",
        "target": r"target.*?(?:KES|Kes)?\s*([\d,]+\.?\d*)\s*(?:billion|million)?",
    }
    
    def __init__(self):
        """Initialize parser."""
        self.records: List[TaxRevenueRecord] = []
    
    def parse_pdf(self, pdf_path: str) -> List[TaxRevenueRecord]:
        """
        Parse KRA press release PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            list: Extracted tax revenue records
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            
            logger.info(f"Extracted {len(text)} characters from {pdf_path}")
            
            # Parse extracted text
            records = self.parse_text(text, source_url=pdf_path)
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to parse PDF {pdf_path}: {str(e)}")
            raise
    
    def parse_text(
        self,
        text: str,
        source_url: str = None
    ) -> List[TaxRevenueRecord]:
        """
        Parse text to extract revenue figures.
        
        Args:
            text: Press release text
            source_url: Source document URL
            
        Returns:
            list: Extracted records
        """
        records = []
        
        # Extract report date
        report_date = self._extract_date(text)
        
        # Extract revenue figures
        revenue_matches = re.finditer(
            self.PATTERNS["revenue_statement"],
            text,
            re.IGNORECASE
        )
        
        for match in revenue_matches:
            tax_head_name = match.group(1).strip()
            amount_str = match.group(2).replace(",", "")
            
            try:
                amount = float(amount_str)
                
                # Convert billions/millions to base units
                if "billion" in match.group(0).lower():
                    amount *= 1_000_000_000
                elif "million" in match.group(0).lower():
                    amount *= 1_000_000
                
                # Map to tax head enum
                tax_head = self._map_tax_head(tax_head_name)
                
                record = TaxRevenueRecord(
                    report_date=report_date,
                    tax_head=tax_head,
                    collection_amount=amount,
                    source_url=source_url
                )
                
                records.append(record)
                
                logger.info(
                    f"Extracted: {tax_head.value} = KES {amount:,.0f} ({report_date})"
                )
                
            except ValueError:
                logger.warning(f"Could not parse amount: {amount_str}")
                continue
        
        return records
    
    def _extract_date(self, text: str) -> datetime:
        """Extract report date from text."""
        match = re.search(self.PATTERNS["date"], text)
        
        if match:
            month_str = match.group(1)
            year_str = match.group(2)
            
            # Parse date
            try:
                date_str = f"{month_str} {year_str}"
                return datetime.strptime(date_str, "%B %Y")
            except ValueError:
                logger.warning(f"Could not parse date: {date_str}")
        
        return datetime.now()
    
    @staticmethod
    def _map_tax_head(tax_head_name: str) -> TaxHead:
        """Map text to tax head enum."""
        name_lower = tax_head_name.lower()
        
        mapping = {
            "income": TaxHead.INCOME_TAX,
            "vat": TaxHead.VAT,
            "excise": TaxHead.EXCISE,
            "custom": TaxHead.CUSTOMS,
            "corporation": TaxHead.CORPORATION_TAX,
            "withholding": TaxHead.WITHHOLDING_TAX,
            "stamp": TaxHead.STAMP_DUTY,
        }
        
        for key, tax_head in mapping.items():
            if key in name_lower:
                return tax_head
        
        logger.warning(f"Unknown tax head: {tax_head_name}")
        return TaxHead.OTHER


class TaxRevenueAnalyzer:
    """Analyze extracted KRA revenue data."""
    
    @staticmethod
    def calculate_collection_rate(
        actual: float,
        target: float
    ) -> float:
        """Calculate collection rate as percentage of target."""
        return (actual / target * 100) if target > 0 else 0
    
    @staticmethod
    def calculate_growth_rate(
        current: float,
        previous: float
    ) -> float:
        """Calculate year-on-year growth rate."""
        return ((current - previous) / abs(previous)) * 100 if previous != 0 else 0
    
    @staticmethod
    def summarize_by_tax_head(
        records: List[TaxRevenueRecord]
    ) -> Dict[TaxHead, Dict]:
        """Summarize records by tax head."""
        summary = {}
        
        for record in records:
            if record.tax_head not in summary:
                summary[record.tax_head] = {
                    "total": 0,
                    "count": 0,
                    "avg": 0
                }
            
            summary[record.tax_head]["total"] += record.collection_amount
            summary[record.tax_head]["count"] += 1
        
        # Calculate averages
        for tax_head in summary:
            if summary[tax_head]["count"] > 0:
                summary[tax_head]["avg"] = (
                    summary[tax_head]["total"] / summary[tax_head]["count"]
                )
        
        return summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    parser = PressReleaseParser()
    print("KRA press release parser module loaded")
