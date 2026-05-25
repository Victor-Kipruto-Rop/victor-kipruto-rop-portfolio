with staging as (
    select * from {{ ref('stg_absa_quarterly') }}
),

capital_metrics as (
    select
        year,
        max(case when indicator = 'Total Capital' then value_m_kes end) as total_capital,
        max(case when indicator = 'Risk-Weighted Assets' then value_m_kes end) as risk_weighted_assets
    from staging
    group by 1
),

calculated as (
    select
        year,
        total_capital,
        risk_weighted_assets,
        (total_capital / nullif(risk_weighted_assets, 0)) * 100 as car_percentage
    from capital_metrics
)

select * from calculated
