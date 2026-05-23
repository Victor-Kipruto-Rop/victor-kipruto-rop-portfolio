with staging as (
    select * from {{ ref('stg_absa_quarterly') }}
),

asset_metrics as (
    select
        period,
        max(case when metric_name = 'Non-Performing Loans' then metric_value end) as npl_amount,
        max(case when metric_name = 'Gross Loans' then metric_value end) as gross_loans
    from staging
    group by 1
),

calculated as (
    select
        period,
        npl_amount,
        gross_loans,
        (npl_amount / nullif(gross_loans, 0)) * 100 as npl_ratio_percentage
    from asset_metrics
)

select * from calculated
