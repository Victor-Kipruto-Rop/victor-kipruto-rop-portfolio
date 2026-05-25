"""
AML Structuring Detector - Identifies suspicious splitting of transactions

Detects "structuring" or "smurfing" where customers split large transactions
into smaller amounts below reporting thresholds to evade detection.
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class StructuringAlert:
    """Alert for potential structuring activity."""
    alert_id: str
    customer_id: str
    detection_type: str  # "structuring" or "smurfing"
    risk_score: float
    transactions: List[Dict]
    pattern_description: str
    generated_at: datetime


class StructuringDetector:
    """
    Detect potential structuring/smurfing patterns.
    
    Rules:
    - Multiple transactions totaling > threshold
    - Transactions just below reporting threshold (KES 1M for Kenya)
    - Pattern of regular structured deposits followed by withdrawals
    - Multiple customers sending to same beneficiary
    - Transactions from same source to multiple destinations
    """
    
    # Configuration
    REPORTING_THRESHOLD = 1_000_000  # KES 1M
    STRUCTURING_THRESHOLD = REPORTING_THRESHOLD * 0.95  # 95% of threshold
    TIME_WINDOW_DAYS = 7
    MIN_TRANSACTION_COUNT = 3
    
    def __init__(self):
        """Initialize detector."""
        self.customer_transactions: Dict[str, List[Dict]] = defaultdict(list)
    
    def add_transaction(self, transaction: Dict) -> None:
        """
        Register a transaction for analysis.
        
        Args:
            transaction: Transaction record with customer_id, amount, timestamp, etc.
        """
        customer_id = transaction.get("customer_id")
        if customer_id:
            self.customer_transactions[customer_id].append(transaction)
    
    def detect_structured_deposits(
        self,
        customer_id: str,
        days_window: int = 7
    ) -> Optional[StructuringAlert]:
        """
        Detect structured deposits pattern.
        
        Identifies multiple deposits, each just below threshold, totaling
        a large amount within a short time window.
        
        Args:
            customer_id: Customer to analyze
            days_window: Time window in days
            
        Returns:
            StructuringAlert if pattern detected, None otherwise
        """
        transactions = self.customer_transactions.get(customer_id, [])
        
        if not transactions:
            return None
        
        # Filter recent transactions
        cutoff_date = datetime.now() - timedelta(days=days_window)
        recent_txns = [
            t for t in transactions
            if t.get("type") == "deposit" and
            datetime.fromisoformat(t.get("timestamp", "")) >= cutoff_date
        ]
        
        if len(recent_txns) < self.MIN_TRANSACTION_COUNT:
            return None
        
        # Check if amounts are suspiciously close to threshold
        suspicious_count = sum(
            1 for t in recent_txns
            if self.STRUCTURING_THRESHOLD <= t.get("amount", 0) <= self.REPORTING_THRESHOLD
        )
        
        total_amount = sum(t.get("amount", 0) for t in recent_txns)
        
        if suspicious_count >= self.MIN_TRANSACTION_COUNT and total_amount > self.REPORTING_THRESHOLD:
            risk_score = min(100, (suspicious_count / len(recent_txns)) * 100)
            
            alert = StructuringAlert(
                alert_id=f"STR_{customer_id}_{datetime.now().timestamp()}",
                customer_id=customer_id,
                detection_type="structuring",
                risk_score=risk_score,
                transactions=recent_txns,
                pattern_description=(
                    f"Detected {suspicious_count} deposits of "
                    f"{self.STRUCTURING_THRESHOLD:,.0f}-{self.REPORTING_THRESHOLD:,.0f} KES "
                    f"totaling {total_amount:,.0f} KES in {days_window} days"
                ),
                generated_at=datetime.now()
            )
            
            logger.warning(f"🚨 Structuring alert: {alert.alert_id}")
            return alert
        
        return None
    
    def detect_rapid_cycles(
        self,
        customer_id: str,
        days_window: int = 7
    ) -> Optional[StructuringAlert]:
        """
        Detect rapid deposit-withdrawal cycles (layering).
        
        Args:
            customer_id: Customer to analyze
            days_window: Time window in days
            
        Returns:
            StructuringAlert if pattern detected
        """
        transactions = self.customer_transactions.get(customer_id, [])
        
        if not transactions:
            return None
        
        # Filter recent transactions
        cutoff_date = datetime.now() - timedelta(days=days_window)
        recent_txns = sorted(
            [
                t for t in transactions
                if datetime.fromisoformat(t.get("timestamp", "")) >= cutoff_date
            ],
            key=lambda x: x.get("timestamp", "")
        )
        
        if len(recent_txns) < self.MIN_TRANSACTION_COUNT:
            return None
        
        # Detect deposit-withdrawal alternation
        deposit_withdrawal_pairs = 0
        
        for i in range(len(recent_txns) - 1):
            current = recent_txns[i]
            next_txn = recent_txns[i + 1]
            
            current_type = current.get("type")
            next_type = next_txn.get("type")
            
            # Check for alternation
            if (current_type == "deposit" and next_type == "withdrawal") or \
               (current_type == "withdrawal" and next_type == "deposit"):
                
                # Check timing (within 24 hours)
                time_diff = (
                    datetime.fromisoformat(next_txn.get("timestamp", "")) -
                    datetime.fromisoformat(current.get("timestamp", ""))
                ).total_seconds() / 3600
                
                if 0 < time_diff <= 24:
                    deposit_withdrawal_pairs += 1
        
        if deposit_withdrawal_pairs >= 2:
            risk_score = min(100, deposit_withdrawal_pairs * 20)
            
            alert = StructuringAlert(
                alert_id=f"CYC_{customer_id}_{datetime.now().timestamp()}",
                customer_id=customer_id,
                detection_type="rapid_cycles",
                risk_score=risk_score,
                transactions=recent_txns,
                pattern_description=(
                    f"Detected {deposit_withdrawal_pairs} rapid deposit-withdrawal cycles "
                    f"within {days_window} days (potential layering)"
                ),
                generated_at=datetime.now()
            )
            
            logger.warning(f"🚨 Rapid cycle alert: {alert.alert_id}")
            return alert
        
        return None
    
    def get_customer_risk_profile(
        self,
        customer_id: str,
        analysis_days: int = 90
    ) -> Dict:
        """
        Get overall risk profile for customer.
        
        Args:
            customer_id: Customer ID
            analysis_days: Historical period to analyze
            
        Returns:
            dict: Risk profile metrics
        """
        transactions = self.customer_transactions.get(customer_id, [])
        
        if not transactions:
            return {"risk_level": "unknown"}
        
        # Filter to analysis period
        cutoff_date = datetime.now() - timedelta(days=analysis_days)
        relevant_txns = [
            t for t in transactions
            if datetime.fromisoformat(t.get("timestamp", "")) >= cutoff_date
        ]
        
        # Calculate metrics
        total_deposits = sum(
            t.get("amount", 0) for t in relevant_txns
            if t.get("type") == "deposit"
        )
        
        total_withdrawals = sum(
            t.get("amount", 0) for t in relevant_txns
            if t.get("type") == "withdrawal"
        )
        
        large_transactions = sum(
            1 for t in relevant_txns
            if t.get("amount", 0) > self.REPORTING_THRESHOLD
        )
        
        suspicious_transactions = sum(
            1 for t in relevant_txns
            if self.STRUCTURING_THRESHOLD <= t.get("amount", 0) <= self.REPORTING_THRESHOLD
        )
        
        return {
            "customer_id": customer_id,
            "analysis_period_days": analysis_days,
            "transaction_count": len(relevant_txns),
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "net_flow": total_deposits - total_withdrawals,
            "large_transactions": large_transactions,
            "suspicious_structured_txns": suspicious_transactions,
            "structuring_risk_score": (suspicious_transactions / len(relevant_txns) * 100) if relevant_txns else 0,
            "risk_level": self._assess_risk_level(
                suspicious_transactions,
                large_transactions,
                len(relevant_txns)
            )
        }
    
    @staticmethod
    def _assess_risk_level(
        suspicious_count: int,
        large_count: int,
        total_count: int
    ) -> str:
        """Assess overall risk level."""
        if total_count == 0:
            return "unknown"
        
        suspicious_ratio = suspicious_count / total_count
        
        if suspicious_ratio > 0.5 or suspicious_count > 5:
            return "high"
        elif suspicious_ratio > 0.2 or suspicious_count > 2:
            return "medium"
        else:
            return "low"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    detector = StructuringDetector()
    print("Structuring detector module loaded")
