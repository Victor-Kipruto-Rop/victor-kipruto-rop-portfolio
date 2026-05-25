import pandas as pd
import os
from sqlalchemy import create_engine

def create_all_snapshots():
    # Mapping
    project_configs = {
        "KCB_Group(ETL)/Financial_Performance_Tracker": {
            "db": "kcb_financials", "port": 5436, "user": "kcb_admin", "pass": "kcb_password",
            "tables": ["mart_subsidiary_performance", "mart_nim_trend", "mart_roe_roa", "mart_subsidiary_perf", "mart_npl_ratio"]
        },
        "KCB_Group(ETL)/MPesa_Loan_Book_Analytics": {
            "db": "kcb_mpesa", "port": 5436, "user": "kcb_admin", "pass": "kcb_password",
            "tables": ["mart_vintage_analysis", "mart_loan_cohorts", "mart_collection_efficiency"]
        },
        "Kenya_Banking_Sector/Consolidated_Data_Warehouse": {
            "db": "sector_dwh", "port": 5437, "user": "sector_admin", "pass": "sector_password",
            "tables": ["mart_sector_kpis"]
        },
        "KRA(DATA ENGINEERING)/Tax_Revenue_Analytics": {
            "db": "kra_warehouse", "port": 5438, "user": "kra_admin", "pass": "kra_password",
            "tables": ["mart_revenue_by_tax_head", "mart_target_vs_actual", "mart_gdp_growth", "mart_gdp_tax_ratio"]
        },
        "KRA(DATA ENGINEERING)/Customs_Trade_Pipeline": {
            "db": "kra_warehouse", "port": 5438, "user": "kra_admin", "pass": "kra_password",
            "tables": ["mart_duty_collection", "mart_trade_balance", "mart_trade_by_hs_code"]
        },
        "Absa_Bank_Kenya(PIPELINE)/Financial_KPIs_Warehouse": {
             "db": "absa_warehouse", "port": 5432, "user": "absa_admin", "pass": "absa_password",
             "tables": ["mart_profitability", "mart_efficiency_ratio", "mart_asset_quality", "mart_capital_adequacy"]
        },
        "Safaricom(PIPELINE)": {
             "db": "safaricom_warehouse", "port": 5439, "user": "saf_admin", "pass": "saf_password",
             "tables": ["mart_financial_results", "mart_segment_revenue", "mart_fuliza_performance", "mart_network_quality", "mart_bonga_loyalty"]
        }
    }

    for project_path, config in project_configs.items():
        print(f"\n--- Snapshots for {project_path} ---")
        try:
            host = "localhost"
            engine = create_engine(f"postgresql://{config['user']}:{config['pass']}@{host}:{config['port']}/{config['db']}")
            
            # For Absa, the snapshots are expected in a specific folder relative to root if we follow previous patterns
            if "Absa" in project_path:
                snapshot_dir = "Absa_Bank_Kenya(PIPELINE)/dashboards/snapshots"
            else:
                snapshot_dir = os.path.join(project_path, "dashboards/snapshots")
                
            os.makedirs(snapshot_dir, exist_ok=True)
            
            for table in config['tables']:
                df = pd.read_sql(f"SELECT * FROM {table}", engine)
                df.to_csv(os.path.join(snapshot_dir, f"{table}.csv"), index=False)
                print(f"Success: {table}.csv")
        except Exception as e:
            print(f"Error in {project_path}: {e}")

    # Fallback/Generation for Equity if DB not running
    print("\n--- Processing Equity with CSV mapping ---")
    equity_csv = "Equity_Group(PIPELINE_ETL)/Pan_Africa_Financial_Platform/ingestion/equity_subsidiary_performance.csv"
    if os.path.exists(equity_csv):
        raw_equity = pd.read_csv(equity_csv)
        equity_snap_dir = "Equity_Group(PIPELINE_ETL)/dashboards/snapshots"
        os.makedirs(equity_snap_dir, exist_ok=True)
        raw_equity.to_csv(f"{equity_snap_dir}/mart_subsidiary_performance.csv", index=False)
        print("Equity Snapshot Created (Generated)")

if __name__ == "__main__":
    create_all_snapshots()
