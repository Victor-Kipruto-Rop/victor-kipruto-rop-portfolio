import pandas as pd
import os
from sqlalchemy import create_engine

def create_all_snapshots():
    # Mapping
    project_configs = {
        "KCB_Group(ETL)/Financial_Performance_Tracker": {
            "db": "kcb_financials", "port": 5436, "user": "kcb_admin", "pass": "kcb_password",
            "tables": ["mart_subsidiary_performance", "mart_nim_trend", "mart_roe_roa", "mart_subsidiary_perf"]
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
            "tables": ["mart_revenue_by_tax_head", "mart_target_vs_actual", "macro_economic_indicators"]
        },
        "KRA(DATA ENGINEERING)/Customs_Trade_Pipeline": {
            "db": "kra_warehouse", "port": 5438, "user": "kra_admin", "pass": "kra_password",
            "tables": ["mart_duty_collection", "mart_trade_balance"]
        }
    }

    for project_path, config in project_configs.items():
        print(f"\n--- Snapshots for {project_path} ---")
        try:
            engine = create_engine(f"postgresql://{config['user']}:{config['pass']}@localhost:{config['port']}/{config['db']}")
            snapshot_dir = os.path.join(project_path, "dashboards/snapshots")
            os.makedirs(snapshot_dir, exist_ok=True)
            
            for table in config['tables']:
                df = pd.read_sql(f"SELECT * FROM {table}", engine)
                df.to_csv(os.path.join(snapshot_dir, f"{table}.csv"), index=False)
                print(f"Success: {table}.csv")
        except Exception as e:
            print(f"Error in {project_path}: {e}")

    # Fallback/Generation for Absa & Equity
    print("\n--- Processing Absa/Equity with CSV mapping ---")
    
    # Absa
    absa_csv = "Absa_Bank_Kenya(PIPELINE)/Financial_KPIs_Warehouse/ingestion/absa_robust_financials.csv"
    if os.path.exists(absa_csv):
        raw_absa = pd.read_csv(absa_csv)
        mart_prof = raw_absa.pivot_table(index='year', columns='indicator', values='value_m_kes').reset_index()
        mart_prof.columns.name = None
        mart_prof.rename(columns={'Profit After Tax': 'net_profit', 'Total Assets': 'total_assets', 'Shareholders Equity': 'total_equity'}, inplace=True)
        mart_prof['roa_percent'] = (mart_prof['net_profit'] / mart_prof['total_assets']) * 100
        mart_prof['roe_percent'] = (mart_prof['net_profit'] / mart_prof['total_equity']) * 100
        
        absa_snap_dir = "Absa_Bank_Kenya(PIPELINE)/dashboards/snapshots"
        os.makedirs(absa_snap_dir, exist_ok=True)
        mart_prof.to_csv(f"{absa_snap_dir}/mart_profitability.csv", index=False)
        print("Absa Snapshot Created (Generated)")

    # Equity
    equity_csv = "Equity_Group(PIPELINE_ETL)/Pan_Africa_Financial_Platform/ingestion/equity_subsidiary_performance.csv"
    if os.path.exists(equity_csv):
        raw_equity = pd.read_csv(equity_csv)
        equity_snap_dir = "Equity_Group(PIPELINE_ETL)/dashboards/snapshots"
        os.makedirs(equity_snap_dir, exist_ok=True)
        raw_equity.to_csv(f"{equity_snap_dir}/mart_subsidiary_performance.csv", index=False)
        print("Equity Snapshot Created (Generated)")

if __name__ == "__main__":
    create_all_snapshots()
