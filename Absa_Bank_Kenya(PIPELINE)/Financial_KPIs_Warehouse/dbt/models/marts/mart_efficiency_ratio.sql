with staging as (
    select * from {{ ref('stg_absa_quarterly') }}
),

efficiency_metrics as (
    select
        period,
        max(case when metric_name = 'Operating Expenses' then metric_value end) as operating_expenses,
        max(case when metric_name = 'Total Operating Income' then metric_value end) as total_operating_income
    from staging
    group by 1
),

calculated as (
    select
        period,
        operating_expenses,
        total_operating_income,
        (operating_expenses / nullif(total_operating_income, 0)) * 100 as cost_to_income_ratio
    from efficiency_metrics
)

select * from calculated
