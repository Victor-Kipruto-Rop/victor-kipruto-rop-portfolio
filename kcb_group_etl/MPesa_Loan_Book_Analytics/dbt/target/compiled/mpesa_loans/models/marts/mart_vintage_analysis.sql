with staging as (
    select * from "kcb_mpesa"."public"."stg_mpesa_loans"
),
vintage as (
    select
        cohort_month,
        month_offset,
        amount_disbursed_m_kes,
        amount_repaid_m_kes,
        npl_amount_m_kes,
        (amount_repaid_m_kes / nullif(amount_disbursed_m_kes, 0)) * 100 as repayment_rate_percent,
        (npl_amount_m_kes / nullif(amount_disbursed_m_kes, 0)) * 100 as default_rate_percent
    from staging
)
select * from vintage