with staging as (
    select * from "kcb_financials"."public"."stg_kcb_financials"
),
performance as (
    select
        subsidiary,
        year,
        net_profit_m_kes,
        total_assets_m_kes,
        npl_ratio_percent,
        customer_count,
        (net_profit_m_kes / nullif(total_assets_m_kes, 0)) * 100 as roa_percent,
        lag(net_profit_m_kes) over (partition by subsidiary order by year) as prev_year_profit,
        ((net_profit_m_kes - lag(net_profit_m_kes) over (partition by subsidiary order by year)) / 
            nullif(lag(net_profit_m_kes) over (partition by subsidiary order by year), 0)) * 100 as profit_growth_percent
    from staging
)
select * from performance