with customers as (
    select * from "pan_africa_platform"."public"."stg_customers"
),
subsidiaries as (
    select * from "pan_africa_platform"."public"."stg_subsidiary_meta"
),
regional_stats as (
    select
        s.country,
        s.region,
        count(c.customer_id) as total_customers,
        avg(c.digital_engagement_score) as avg_digital_score,
        (sum(case when c.loan_status = 'Active Loan' then 1 else 0 end)::float / nullif(count(c.customer_id), 0)) * 100 as loan_penetration_pct,
        (sum(case when c.credit_score_bucket in ('Poor (300-579)', 'Very Poor (<300)') then 1 else 0 end)::float / nullif(count(c.customer_id), 0)) * 100 as high_risk_pct,
        sum(c.account_balance_usd) as total_deposits_usd
    from subsidiaries s
    left join customers c on s.subsidiary_name = c.subsidiary_name
    group by 1, 2
)
select * from regional_stats