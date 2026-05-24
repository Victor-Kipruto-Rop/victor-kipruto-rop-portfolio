-- Dashboard: Open Banking Insights
-- Database: absa_open_banking

-- 1. Daily Transaction Volume
SELECT activity_date, total_volume 
FROM mart_customer_activity 
ORDER BY activity_date;

-- 2. Transaction Count per Account
SELECT account_id, sum(transaction_count) as total_txns
FROM mart_customer_activity
GROUP BY 1;
