with staging as (
    select * from {{ ref('stg_mpesa_loans') }}
),
performance as (
    select
        cohort_month,
        max(month_offset) as latest_offset,
        max(amount_disbursed_m_kes) as total_disbursed,
        max(npl_amount_m_kes) / nullif(max(amount_disbursed_m_kes), 0) * 100 as final_default_rate
    from staging
    group by cohort_month
)
select * from performance
