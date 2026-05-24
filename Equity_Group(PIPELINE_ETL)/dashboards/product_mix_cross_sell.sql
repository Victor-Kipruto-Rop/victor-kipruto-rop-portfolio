-- Dashboard: Product Mix & Cross-Sell
-- Database: equitel_analytics

-- 1. Cross-Sell Penetration (Insurance vs Investments)
SELECT 
    period, 
    insurance_cross_sell_rate, 
    investment_cross_sell_rate 
FROM mart_cross_sell_rate 
ORDER BY period;

-- 2. User Segmentation (Product Mix)
SELECT 
    period, 
    insurance_subscribers, 
    investment_subscribers, 
    pure_mobile_users 
FROM mart_product_mix 
ORDER BY period;
