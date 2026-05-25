import pytest
from datetime import datetime
from ingestion.consolidation_engine import ConsolidationEngine, Subsidiary, FinancialMetric, SubsidiaryFinancial

def test_consolidation_engine_totals():
    engine = ConsolidationEngine()
    
    # Add mock data for Kenya
    kenya_data = SubsidiaryFinancial(
        subsidiary=Subsidiary.KCB_BANK_KENYA,
        reporting_period="2024-01",
        metrics={
            FinancialMetric.NET_PROFIT: 1000.0,
            FinancialMetric.TOTAL_ASSETS: 10000.0,
            FinancialMetric.SHAREHOLDERS_EQUITY: 2000.0
        },
        source="internal_report",
        reported_date=datetime.now()
    )
    
    # Add mock data for Tanzania
    tz_data = SubsidiaryFinancial(
        subsidiary=Subsidiary.KDBANK,
        reporting_period="2024-01",
        metrics={
            FinancialMetric.NET_PROFIT: 200.0,
            FinancialMetric.TOTAL_ASSETS: 2000.0,
            FinancialMetric.SHAREHOLDERS_EQUITY: 500.0
        },
        source="internal_report",
        reported_date=datetime.now()
    )
    
    engine.add_subsidiary_financials(kenya_data)
    engine.add_subsidiary_financials(tz_data)
    
    consolidated = engine.consolidate_metrics("2024-01")
    
    assert consolidated[FinancialMetric.NET_PROFIT] == 1200.0
    assert consolidated[FinancialMetric.TOTAL_ASSETS] == 12000.0

def test_group_ratios():
    engine = ConsolidationEngine()
    consolidated_metrics = {
        FinancialMetric.NET_PROFIT: 1000.0,
        FinancialMetric.TOTAL_ASSETS: 10000.0,
        FinancialMetric.SHAREHOLDERS_EQUITY: 5000.0
    }
    
    ratios = engine.calculate_group_ratios(consolidated_metrics)
    
    assert ratios["roa"] == 10.0  # (1000/10000) * 100
    assert ratios["roe"] == 20.0  # (1000/5000) * 100
