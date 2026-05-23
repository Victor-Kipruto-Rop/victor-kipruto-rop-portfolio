with staging as (
    select * from {{ ref('stg_absa_quarterly') }}
),

capital_metrics as (
    select
        period,
        max(case when metric_name = 'Total Capital' then metric_value end) as total_capital,
        max(case when metric_name = 'Risk-Weighted Assets' then metric_value end) as risk_weighted_assets
    from staging
    group by 1
),

calculated as (
    select
        period,
        total_capital,
        risk_weighted_assets,
        (total_capital / nullif(risk_weighted_assets, 0)) * 100 as car_percentage
    from capital_metrics
)

select * from calculated
