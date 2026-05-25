import pandas as pd
import os

class AMLRulesEngine:
    def __init__(self, data_path="Kenya_Banking_Sector/AML_Transaction_Monitoring/data/synthetic_transactions.csv"):
        self.data_path = data_path
        if os.path.exists(data_path):
            self.df = pd.read_csv(data_path)
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        else:
            self.df = pd.DataFrame()

    def run_structuring_rule(self):
        """Rule: Identify accounts with >3 cash deposits between 900k and 1M within 48 hours."""
        if self.df.empty: return []
        
        cash_txns = self.df[self.df['txn_type'] == 'Cash Deposit']
        near_limit = cash_txns[(cash_txns['amount'] >= 900000) & (cash_txns['amount'] < 1000000)]
        
        alerts = []
        for acc_id, group in near_limit.groupby('account_id'):
            if len(group) >= 3:
                # Basic clustering logic
                alerts.append({
                    "account_id": acc_id,
                    "rule": "Structuring Detected",
                    "severity": "High",
                    "details": f"{len(group)} cash deposits near limit detected."
                })
        return alerts

    def run_pep_rule(self):
        """Rule: Identify high-value transactions involving PEPs."""
        if self.df.empty: return []
        
        pep_txns = self.df[self.df['is_pep'] == True]
        high_value_pep = pep_txns[pep_txns['amount'] > 500000]
        
        alerts = []
        for _, row in high_value_pep.iterrows():
            alerts.append({
                "account_id": row['account_id'],
                "rule": "PEP High-Value Activity",
                "severity": "Medium",
                "details": f"PEP account transacted {row['amount']:,.2f} KES."
            })
        return alerts

    def get_all_alerts(self):
        return self.run_structuring_rule() + self.run_pep_rule()

if __name__ == "__main__":
    engine = AMLRulesEngine()
    alerts = engine.get_all_alerts()
    print(f"Total Alerts Generated: {len(alerts)}")
