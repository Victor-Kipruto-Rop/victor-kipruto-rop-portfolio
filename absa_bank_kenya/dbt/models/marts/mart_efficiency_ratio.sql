with staging as (
    select * from {{ ref('stg_absa_quarterly') }}
),
pivoted as (
    select
        year,
        max(case when indicator = 'Net Interest Income' then value_m_kes end) as nii,
        max(case when indicator = 'Non-Interest Income' then value_m_kes end) as non_int_income,
        max(case when indicator = 'Operating Expenses' then value_m_kes end) as opex
    from staging
    group by 1
),
ratios as (
    select
        year,
        (opex / nullif((nii + non_int_income), 0)) * 100 as cost_to_income_ratio
    from pivoted
)
select * from ratios
