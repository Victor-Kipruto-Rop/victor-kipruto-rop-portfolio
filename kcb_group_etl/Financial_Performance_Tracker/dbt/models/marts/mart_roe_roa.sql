with staging as (
    select * from {{ ref('stg_kcb_financials') }}
),
profitability as (
    select
        subsidiary,
        year,
        net_profit_m_kes,
        total_assets_m_kes,
        shareholders_equity_m_kes,
        (net_profit_m_kes / nullif(total_assets_m_kes, 0)) * 100 as roa_percent,
        (net_profit_m_kes / nullif(shareholders_equity_m_kes, 0)) * 100 as roe_percent
    from staging
)
select * from profitability
