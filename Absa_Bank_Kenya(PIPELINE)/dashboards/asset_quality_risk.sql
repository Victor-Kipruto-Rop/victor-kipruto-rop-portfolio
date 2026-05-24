-- Dashboard: Asset Quality & Risk
-- Database: absa_warehouse

-- 1. Non-Performing Loan (NPL) Ratio Trend
SELECT period, npl_ratio_percentage 
FROM mart_asset_quality 
ORDER BY period;

-- 2. Capital Adequacy Ratio (CAR) vs Regulatory Minimum (14.5%)
SELECT 
    period, 
    car_percentage,
    14.5 as regulatory_minimum
FROM mart_capital_adequacy 
ORDER BY period;
