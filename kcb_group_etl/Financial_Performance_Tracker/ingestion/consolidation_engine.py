"""
KCB Financial Performance Tracker - Subsidiary Consolidation

Consolidates financial statements from KCB subsidiaries (KCB Bank Kenya, KCB Kenya Reinsurance,
etc.) for group-level reporting and analysis.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class Subsidiary(Enum):
    """KCB Group subsidiaries."""
    KCB_BANK_KENYA = "kcb_bank_kenya"
    KCB_REINSURANCE = "kcb_reinsurance"
    KCB_BANCASSURANCE = "kcb_bancassurance"
    KCB_CAPITAL = "kcb_capital"
    KDBANK = "kdbank"


class FinancialMetric(Enum):
    """Financial metrics for consolidation."""
    TOTAL_ASSETS = "total_assets"
    TOTAL_LIABILITIES = "total_liabilities"
    SHAREHOLDERS_EQUITY = "shareholders_equity"
    NET_INTEREST_INCOME = "net_interest_income"
    NON_INTEREST_INCOME = "non_interest_income"
    OPERATING_EXPENSES = "operating_expenses"
    NET_PROFIT = "net_profit"
    LOANS_PORTFOLIO = "loans_portfolio"
    DEPOSITS = "deposits"
    CAPITAL_ADEQUACY_RATIO = "car"
    RETURN_ON_EQUITY = "roe"
    RETURN_ON_ASSETS = "roa"


@dataclass
class SubsidiaryFinancial:
    """Financial data for a subsidiary."""
    subsidiary: Subsidiary
    reporting_period: str  # YYYY-MM format
    metrics: Dict[FinancialMetric, float]
    source: str  # Financial statement source
    reported_date: datetime


class ConsolidationEngine:
    """
    Consolidate subsidiary financial statements.
    
    Handles:
    - Intra-group eliminations
    - Currency translations (for foreign subsidiaries)
    - Minority interest calculations
    - Group ratios and metrics
    """
    
    def __init__(self):
        """Initialize consolidation engine."""
        self.subsidiaries_data: Dict[Subsidiary, List[SubsidiaryFinancial]] = {
            sub: [] for sub in Subsidiary
        }
    
    def add_subsidiary_financials(self, financials: SubsidiaryFinancial) -> None:
        """
        Add subsidiary financial data.
        
        Args:
            financials: Subsidiary financial record
        """
        subsidiary = financials.subsidiary
        self.subsidiaries_data[subsidiary].append(financials)
        
        logger.info(
            f"Added financials for {subsidiary.value} - {financials.reporting_period}"
        )
    
    def consolidate_metrics(
        self,
        reporting_period: str
    ) -> Dict[FinancialMetric, float]:
        """
        Consolidate metrics across all subsidiaries.
        
        Args:
            reporting_period: Period to consolidate (YYYY-MM)
            
        Returns:
            dict: Consolidated metrics
        """
        consolidated = {}
        
        # Collect data for the period
        period_data: Dict[Subsidiary, SubsidiaryFinancial] = {}
        
        for subsidiary, financials_list in self.subsidiaries_data.items():
            for financials in financials_list:
                if financials.reporting_period == reporting_period:
                    period_data[subsidiary] = financials
                    break
        
        if not period_data:
            logger.warning(f"No data found for period {reporting_period}")
            return {}
        
        # Sum metrics across subsidiaries
        all_metrics = set()
        for sub_data in period_data.values():
            all_metrics.update(sub_data.metrics.keys())
        
        for metric in all_metrics:
            total = 0
            count = 0
            
            for sub_data in period_data.values():
                if metric in sub_data.metrics:
                    total += sub_data.metrics[metric]
                    count += 1
            
            if count > 0:
                consolidated[metric] = total
        
        return consolidated
    
    def calculate_group_ratios(
        self,
        consolidated_metrics: Dict[FinancialMetric, float]
    ) -> Dict[str, float]:
        """
        Calculate group-level financial ratios.
        
        Args:
            consolidated_metrics: Consolidated financial metrics
            
        Returns:
            dict: Calculated ratios
        """
        ratios = {}
        
        try:
            # Asset quality
            if FinancialMetric.TOTAL_ASSETS in consolidated_metrics:
                total_assets = consolidated_metrics[FinancialMetric.TOTAL_ASSETS]
                
                if FinancialMetric.LOANS_PORTFOLIO in consolidated_metrics:
                    loans = consolidated_metrics[FinancialMetric.LOANS_PORTFOLIO]
                    ratios["loan_to_asset_ratio"] = loans / total_assets if total_assets > 0 else 0
                
                if FinancialMetric.DEPOSITS in consolidated_metrics:
                    deposits = consolidated_metrics[FinancialMetric.DEPOSITS]
                    ratios["deposit_to_asset_ratio"] = deposits / total_assets if total_assets > 0 else 0
            
            # Profitability
            if FinancialMetric.NET_PROFIT in consolidated_metrics:
                net_profit = consolidated_metrics[FinancialMetric.NET_PROFIT]
                
                if FinancialMetric.TOTAL_ASSETS in consolidated_metrics:
                    total_assets = consolidated_metrics[FinancialMetric.TOTAL_ASSETS]
                    ratios["roa"] = (net_profit / total_assets * 100) if total_assets > 0 else 0
                
                if FinancialMetric.SHAREHOLDERS_EQUITY in consolidated_metrics:
                    equity = consolidated_metrics[FinancialMetric.SHAREHOLDERS_EQUITY]
                    ratios["roe"] = (net_profit / equity * 100) if equity > 0 else 0
            
            # Net Interest Margin
            if FinancialMetric.NET_INTEREST_INCOME in consolidated_metrics and \
               FinancialMetric.TOTAL_ASSETS in consolidated_metrics:
                nii = consolidated_metrics[FinancialMetric.NET_INTEREST_INCOME]
                total_assets = consolidated_metrics[FinancialMetric.TOTAL_ASSETS]
                ratios["nim"] = (nii / total_assets * 100) if total_assets > 0 else 0
            
            # Efficiency
            if FinancialMetric.OPERATING_EXPENSES in consolidated_metrics and \
               FinancialMetric.NON_INTEREST_INCOME in consolidated_metrics:
                opex = consolidated_metrics[FinancialMetric.OPERATING_EXPENSES]
                non_int_income = consolidated_metrics[FinancialMetric.NON_INTEREST_INCOME]
                total_income = (
                    consolidated_metrics.get(FinancialMetric.NET_INTEREST_INCOME, 0) +
                    non_int_income
                )
                ratios["cost_to_income"] = (opex / total_income * 100) if total_income > 0 else 0
            
            logger.info(f"Calculated {len(ratios)} group ratios")
            
        except Exception as e:
            logger.error(f"Error calculating ratios: {str(e)}")
        
        return ratios
    
    def identify_eliminations(
        self,
        subsidiary1: Subsidiary,
        subsidiary2: Subsidiary,
        intergroup_transactions: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Identify and calculate intra-group transactions to eliminate.
        
        Args:
            subsidiary1: First subsidiary
            subsidiary2: Second subsidiary
            intergroup_transactions: Dictionary of transaction amounts
            
        Returns:
            dict: Elimination adjustments
        """
        eliminations = {}
        
        for transaction_type, amount in intergroup_transactions.items():
            # Record eliminations for both sides of transaction
            key = f"{subsidiary1.value}_{subsidiary2.value}_{transaction_type}"
            eliminations[key] = amount
            
            logger.info(
                f"Elimination recorded: {transaction_type} between "
                f"{subsidiary1.value} and {subsidiary2.value}: KES {amount:,.0f}"
            )
        
        return eliminations


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    engine = ConsolidationEngine()
    print("KCB consolidation engine module loaded")
