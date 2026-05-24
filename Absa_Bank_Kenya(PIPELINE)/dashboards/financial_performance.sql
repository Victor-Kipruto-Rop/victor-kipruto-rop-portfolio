-- Dashboard: Financial Performance Overview
-- Database: absa_warehouse

-- 1. Net Interest Margin (NIM) Trend
SELECT period, nim_percentage 
FROM mart_profitability 
ORDER BY period;

-- 2. Return on Equity (ROE) Trend
SELECT period, roe_percentage 
FROM mart_profitability 
ORDER BY period;

-- 3. Cost to Income Ratio (CIR)
SELECT period, cost_to_income_ratio 
FROM mart_efficiency_ratio 
ORDER BY period;
