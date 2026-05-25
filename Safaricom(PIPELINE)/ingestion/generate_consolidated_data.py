import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_safaricom_data():
    print("Generating Safaricom Consolidated Data...")
    
    snapshot_dir = "Safaricom(PIPELINE)/dashboards/snapshots"
    os.makedirs(snapshot_dir, exist_ok=True)
    
    # 1. Financial Results (Annual & Quarterly)
    # 2024 Actuals-ish, 2025 Targets/Estimates
    financials = [
        {"period": "FY 2023", "revenue_m_kes": 310500.0, "ebitda_m_kes": 139500.0, "net_profit_m_kes": 62500.0},
        {"period": "FY 2024", "revenue_m_kes": 335400.0, "ebitda_m_kes": 163800.0, "net_profit_m_kes": 84200.0},
        {"period": "FY 2025 (E)", "revenue_m_kes": 365200.0, "ebitda_m_kes": 178500.0, "net_profit_m_kes": 92100.0}
    ]
    pd.DataFrame(financials).to_csv(f"{snapshot_dir}/mart_financial_results.csv", index=False)
    
    # 2. Segment Revenue
    segments = [
        {"period": "FY 2024", "segment": "M-Pesa", "revenue_m_kes": 117200.0, "contribution": 35.0},
        {"period": "FY 2024", "segment": "Voice", "revenue_m_kes": 81100.0, "contribution": 24.0},
        {"period": "FY 2024", "segment": "Mobile Data", "revenue_m_kes": 54000.0, "contribution": 16.0},
        {"period": "FY 2024", "segment": "Messaging", "revenue_m_kes": 12300.0, "contribution": 4.0},
        {"period": "FY 2024", "segment": "Fixed & Others", "revenue_m_kes": 70800.0, "contribution": 21.0}
    ]
    pd.DataFrame(segments).to_csv(f"{snapshot_dir}/mart_segment_revenue.csv", index=False)
    
    # 3. Fuliza Credit Risk Analytics
    # Monthly cohorts for 2025
    start_date = datetime(2025, 1, 1)
    fuliza_data = []
    for i in range(12):
        date = start_date + timedelta(days=i*30)
        disbursed = 60000.0 + np.random.uniform(-5000, 5000)
        repaid = disbursed * np.random.uniform(0.96, 0.99)
        active_users = 7.5 + np.random.uniform(-0.5, 0.5) # Millions
        fuliza_data.append({
            "month": date.strftime("%Y-%m"),
            "amount_disbursed_m_kes": round(disbursed, 2),
            "amount_repaid_m_kes": round(repaid, 2),
            "active_users_m": round(active_users, 2),
            "npl_ratio_percent": round(100 - (repaid/disbursed*100), 2)
        })
    pd.DataFrame(fuliza_data).to_csv(f"{snapshot_dir}/mart_fuliza_performance.csv", index=False)
    
    # 4. Network Quality Pipeline
    regions = ["Nairobi", "Coast", "Rift Valley", "Central", "Western", "Nyanza", "Eastern"]
    network_data = []
    for r in regions:
        network_data.append({
            "region": r,
            "availability_percent": round(99.8 + np.random.uniform(-0.5, 0.1), 2),
            "latency_ms": round(25 + np.random.uniform(-10, 20), 1),
            "avg_speed_mbps": round(45 + np.random.uniform(-15, 30), 1),
            "cx_score": round(4.2 + np.random.uniform(-0.5, 0.6), 1)
        })
    pd.DataFrame(network_data).to_csv(f"{snapshot_dir}/mart_network_quality.csv", index=False)
    
    # 5. Bonga Loyalty Analytics
    bonga_segments = ["Gold", "Platinum", "Silver", "Bronze"]
    loyalty_data = []
    for s in bonga_segments:
        loyalty_data.append({
            "segment": s,
            "total_points_m": round(np.random.uniform(100, 1000), 1),
            "redemption_rate_percent": round(np.random.uniform(65, 85), 1),
            "active_loyalty_users": int(np.random.uniform(500000, 5000000))
        })
    pd.DataFrame(loyalty_data).to_csv(f"{snapshot_dir}/mart_bonga_loyalty.csv", index=False)
    
    print(f"Successfully generated Safaricom analytical snapshots in {snapshot_dir}")

if __name__ == "__main__":
    generate_safaricom_data()
