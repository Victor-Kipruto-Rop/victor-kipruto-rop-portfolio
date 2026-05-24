-- Dashboard: Pan-Africa Consolidation
-- Database: pan_africa_platform

-- 1. Total Group Profit (USD)
SELECT period, total_profit_usd, subsidiary_count 
FROM mart_group_consolidation 
ORDER BY period;

-- 2. Subsidiary Profit Contribution %
SELECT subsidiary, period, contribution_percentage 
FROM mart_subsidiary_comparison 
ORDER BY period, contribution_percentage DESC;
