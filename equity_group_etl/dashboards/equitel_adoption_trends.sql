-- Dashboard: Equitel Adoption Trends
-- Database: equitel_analytics

-- 1. EazzyPay Transaction Velocity Growth
SELECT period, transaction_count, growth_rate 
FROM mart_adoption_curve 
ORDER BY period;

-- 2. ARPU Benchmark (KES)
SELECT period, arpu_kes 
FROM mart_arpu_benchmark 
ORDER BY period;
