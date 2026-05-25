with staging as (
    select * from "kcb_financials"."public"."stg_kcb_financials"
),
performance as (
    select
        subsidiary,
        year,
        net_profit_m_kes,
        total_assets_m_kes,
        operating_expenses_m_kes,
        (operating_expenses_m_kes / nullif(net_interest_income_m_kes, 0)) * 100 as cost_to_income_ratio,
        customer_count
    from staging
)
select * from performance