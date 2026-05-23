import pandas as pd
import numpy as np
from typing import List, Dict

class CreditScorer:
    """
    Implements a cash-flow based creditworthiness scoring model using open banking transaction data.
    """
    def __init__(self, target_currency: str = "KES"):
        self.target_currency = target_currency

    def calculate_score(self, transactions: List[Dict]) -> Dict:
        """
        Calculates a credit score (0-1000) based on transaction patterns.
        Factors:
        - Monthly income stability
        - Savings rate (surplus)
        - Transaction frequency
        - Debt-to-income ratio (simulated by identifying loan keywords)
        """
        if not transactions:
            return {"score": 0, "rating": "No Data", "insights": ["No transaction history found."]}

        df = pd.DataFrame(transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        # Monthly aggregates
        df['month'] = df['transaction_date'].dt.to_period('M')
        monthly = df.groupby('month')['amount'].agg(['sum', 'count', 
            lambda x: x[x > 0].sum(), # Inflow
            lambda x: x[x < 0].sum()  # Outflow
        ]).rename(columns={'<lambda_0>': 'inflow', '<lambda_1>': 'outflow'})

        # 1. Income Stability (Coefficient of variation of inflows)
        inflows = monthly['inflow']
        stability_score = 0
        if len(inflows) > 1:
            cv = inflows.std() / inflows.mean() if inflows.mean() != 0 else 1
            stability_score = max(0, 300 * (1 - cv))
        else:
            stability_score = 150 # Partial score for short history

        # 2. Savings Rate (Surplus)
        total_inflow = monthly['inflow'].sum()
        total_outflow = abs(monthly['outflow'].sum())
        surplus_ratio = (total_inflow - total_outflow) / total_inflow if total_inflow > 0 else 0
        savings_score = min(300, max(0, surplus_ratio * 1000))

        # 3. Liquidity/Frequency
        frequency_score = min(200, len(df) * 5)

        # 4. Negative Indicators (e.g., Overdraft, Loans - simulated)
        debt_indicators = df[df['description'].str.contains('loan|interest|debt|penalty', case=False, na=False)]
        penalty_factor = max(0, 200 - (len(debt_indicators) * 20))

        final_score = int(stability_score + savings_score + frequency_score + penalty_factor)
        final_score = min(1000, max(0, final_score))

        rating = "Poor"
        if final_score > 800: rating = "Excellent"
        elif final_score > 600: rating = "Good"
        elif final_score > 400: rating = "Fair"

        return {
            "score": final_score,
            "rating": rating,
            "metrics": {
                "monthly_avg_inflow": round(monthly['inflow'].mean(), 2),
                "surplus_ratio": round(surplus_ratio, 2),
                "transaction_count": len(df)
            },
            "insights": self._generate_insights(stability_score, surplus_ratio, len(debt_indicators))
        }

    def _generate_insights(self, stability, surplus, debts):
        insights = []
        if stability < 150: insights.append("Income shows high volatility.")
        if surplus < 0.1: insights.append("Low savings rate detected; high expenditure relative to income.")
        if debts > 2: insights.append("Frequent debt-related transactions observed.")
        if not insights: insights.append("Strong financial behavior across all tracked metrics.")
        return insights

if __name__ == "__main__":
    # Test logic
    scorer = CreditScorer()
    mock_txns = [
        {"transaction_date": "2023-01-05", "amount": 50000, "description": "Salary"},
        {"transaction_date": "2023-01-10", "amount": -10000, "description": "Rent"},
        {"transaction_date": "2023-01-15", "amount": -5000, "description": "Groceries"},
        {"transaction_date": "2023-02-05", "amount": 52000, "description": "Salary"},
        {"transaction_date": "2023-02-12", "amount": -10000, "description": "Rent"},
        {"transaction_date": "2023-02-20", "amount": -2000, "description": "Internet Loan Repayment"}
    ]
    print(scorer.calculate_score(mock_txns))
