"""
Consolidated Banking Data Warehouse - NPL Bridge Reconciliation

Reconciles NPL (Non-Performing Loan) data across CBK supervisory returns,
bank financial statements, and market data to maintain data integrity
in the consolidated data warehouse.
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


@dataclass
class NPLRecord:
    """Non-Performing Loan record."""
    bank_code: str
    reporting_period: str
    npl_gross_amount: Decimal
    npl_net_amount: Decimal
    npl_count: int
    npl_ratio: float
    provision_amount: Decimal
    sector: str  # Sector classification
    source: str  # "cbk_return" or "financial_statement"


class NPLBridgeReconciliation:
    """
    Reconcile NPL data from multiple sources.
    
    Handles:
    - Differences between CBK Form 4 returns and bank-reported figures
    - Classification differences (sector, product type)
    - Timing differences (month-end vs month-end)
    - Provision adequacy analysis
    """
    
    def __init__(self):
        """Initialize reconciliation engine."""
        self.cbk_npl_records: List[NPLRecord] = []
        self.statement_npl_records: List[NPLRecord] = []
        self.reconciliation_results: Dict = {}
    
    def add_cbk_npl_data(self, record: NPLRecord) -> None:
        """
        Add NPL data from CBK supervisory returns.
        
        Args:
            record: NPL record from CBK Form 4
        """
        record.source = "cbk_return"
        self.cbk_npl_records.append(record)
        logger.info(
            f"Added CBK NPL data: {record.bank_code} - {record.reporting_period} - "
            f"KES {record.npl_gross_amount:,.0f}"
        )
    
    def add_statement_npl_data(self, record: NPLRecord) -> None:
        """
        Add NPL data from bank financial statements.
        
        Args:
            record: NPL record from financial statement
        """
        record.source = "financial_statement"
        self.statement_npl_records.append(record)
        logger.info(
            f"Added Statement NPL data: {record.bank_code} - {record.reporting_period} - "
            f"KES {record.npl_gross_amount:,.0f}"
        )
    
    def reconcile_npl_figures(
        self,
        bank_code: str,
        reporting_period: str
    ) -> Dict[str, any]:
        """
        Reconcile NPL figures for a bank and period.
        
        Args:
            bank_code: Bank code
            reporting_period: Period (YYYY-MM)
            
        Returns:
            dict: Reconciliation results
        """
        # Find matching records
        cbk_record = self._find_record(self.cbk_npl_records, bank_code, reporting_period)
        stmt_record = self._find_record(self.statement_npl_records, bank_code, reporting_period)
        
        if not cbk_record or not stmt_record:
            logger.warning(
                f"Missing data for reconciliation: {bank_code} - {reporting_period}"
            )
            return {"status": "incomplete"}
        
        # Calculate differences
        amount_difference = cbk_record.npl_gross_amount - stmt_record.npl_gross_amount
        amount_difference_pct = (
            (amount_difference / cbk_record.npl_gross_amount * 100)
            if cbk_record.npl_gross_amount > 0 else 0
        )
        
        count_difference = cbk_record.npl_count - stmt_record.npl_count
        ratio_difference = cbk_record.npl_ratio - stmt_record.npl_ratio
        
        # Tolerance thresholds
        tolerance_amount_pct = 5.0  # 5% tolerance
        tolerance_ratio = 1.0  # 1% ratio tolerance
        
        reconciliation = {
            "bank_code": bank_code,
            "reporting_period": reporting_period,
            "cbk_npl_amount": float(cbk_record.npl_gross_amount),
            "statement_npl_amount": float(stmt_record.npl_gross_amount),
            "amount_difference": float(amount_difference),
            "amount_difference_pct": amount_difference_pct,
            "cbk_npl_count": cbk_record.npl_count,
            "statement_npl_count": stmt_record.npl_count,
            "count_difference": count_difference,
            "cbk_npl_ratio": cbk_record.npl_ratio,
            "statement_npl_ratio": stmt_record.npl_ratio,
            "ratio_difference": ratio_difference,
            "status": self._determine_status(
                amount_difference_pct,
                tolerance_amount_pct,
                ratio_difference,
                tolerance_ratio
            ),
            "reconciled_amount": self._select_reconciled_amount(
                cbk_record, stmt_record, amount_difference_pct, tolerance_amount_pct
            ),
            "notes": []
        }
        
        # Add explanatory notes
        if abs(amount_difference_pct) > tolerance_amount_pct:
            reconciliation["notes"].append(
                f"Material difference in NPL amounts: {amount_difference_pct:.2f}%"
            )
        
        if abs(ratio_difference) > tolerance_ratio:
            reconciliation["notes"].append(
                f"NPL ratio difference: {ratio_difference:.2f}%"
            )
        
        logger.info(
            f"Reconciliation completed for {bank_code} - Status: {reconciliation['status']}"
        )
        
        return reconciliation
    
    def _find_record(
        self,
        records: List[NPLRecord],
        bank_code: str,
        reporting_period: str
    ) -> Optional[NPLRecord]:
        """Find a specific record in list."""
        for record in records:
            if record.bank_code == bank_code and record.reporting_period == reporting_period:
                return record
        return None
    
    @staticmethod
    def _determine_status(
        amount_diff_pct: float,
        amount_tolerance: float,
        ratio_diff: float,
        ratio_tolerance: float
    ) -> str:
        """Determine reconciliation status."""
        if abs(amount_diff_pct) <= amount_tolerance and abs(ratio_diff) <= ratio_tolerance:
            return "reconciled"
        elif abs(amount_diff_pct) <= amount_tolerance * 1.5:
            return "minor_variance"
        else:
            return "unreconciled"
    
    @staticmethod
    def _select_reconciled_amount(
        cbk_record: NPLRecord,
        stmt_record: NPLRecord,
        diff_pct: float,
        tolerance: float
    ) -> Decimal:
        """Select authoritative amount for warehouse."""
        # If well-reconciled, use average
        if abs(diff_pct) <= tolerance:
            return (cbk_record.npl_gross_amount + stmt_record.npl_gross_amount) / 2
        
        # Otherwise, prefer CBK (regulatory authority)
        return cbk_record.npl_gross_amount
    
    def reconcile_batch(
        self,
        bank_codes: List[str],
        reporting_period: str
    ) -> List[Dict]:
        """
        Reconcile multiple banks for a period.
        
        Args:
            bank_codes: List of bank codes
            reporting_period: Reporting period
            
        Returns:
            list: Reconciliation results for each bank
        """
        results = []
        
        for bank_code in bank_codes:
            result = self.reconcile_npl_figures(bank_code, reporting_period)
            results.append(result)
        
        # Summary statistics
        unreconciled_count = sum(1 for r in results if r.get("status") == "unreconciled")
        logger.info(
            f"Batch reconciliation: {len(results)} banks, "
            f"{unreconciled_count} unreconciled"
        )
        
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    reconciler = NPLBridgeReconciliation()
    print("NPL bridge reconciliation module loaded")
