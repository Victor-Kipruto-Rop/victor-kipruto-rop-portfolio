with staging as (
    select * from {{ ref('stg_absa_quarterly') }}
),

asset_metrics as (
    select
        year,
        max(case when indicator = 'Non-Performing Loans' then value_m_kes end) as npl_amount,
        max(case when indicator = 'Gross Loans' then value_m_kes end) as gross_loans
    from staging
    group by 1
),

calculated as (
    select
        year,
        npl_amount,
        gross_loans,
        (npl_amount / nullif(gross_loans, 0)) * 100 as npl_ratio_percentage
    from asset_metrics
)

select * from calculated
