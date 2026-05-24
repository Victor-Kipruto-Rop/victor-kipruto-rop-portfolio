with staging as (
    select * from {{ ref('stg_absa_quarterly') }}
),
pivoted as (
    select
        year,
        max(case when indicator = 'Total Assets' then value_m_kes end) as total_assets,
        max(case when indicator = 'Profit After Tax' then value_m_kes end) as net_profit,
        max(case when indicator = 'Shareholders Equity' then value_m_kes end) as total_equity
    from staging
    group by 1
),
ratios as (
    select
        year,
        net_profit,
        (net_profit / nullif(total_assets, 0)) * 100 as roa_percent,
        (net_profit / nullif(total_equity, 0)) * 100 as roe_percent
    from pivoted
)
select * from ratios
