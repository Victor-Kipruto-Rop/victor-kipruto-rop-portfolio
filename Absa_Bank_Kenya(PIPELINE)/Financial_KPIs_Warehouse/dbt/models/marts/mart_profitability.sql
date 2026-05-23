with staging as (
    select * from {{ ref('stg_absa_quarterly') }}
),

profitability_metrics as (
    select
        period,
        max(case when metric_name = 'Net Interest Income' then metric_value end) as net_interest_income,
        max(case when metric_name = 'Net Income' then metric_value end) as net_income,
        max(case when metric_name = 'Average Earning Assets' then metric_value end) as avg_earning_assets,
        max(case when metric_name = 'Average Shareholders Equity' then metric_value end) as avg_equity
    from staging
    group by 1
),

calculated as (
    select
        period,
        net_interest_income,
        net_income,
        (net_interest_income / nullif(avg_earning_assets, 0)) * 100 as nim_percentage,
        (net_income / nullif(avg_equity, 0)) * 100 as roe_percentage
    from profitability_metrics
)

select * from calculated
