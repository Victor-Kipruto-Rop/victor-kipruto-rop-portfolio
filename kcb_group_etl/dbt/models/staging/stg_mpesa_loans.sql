with source as (
    select * from {{ source('kcb_raw', 'raw_mpesa_loans') }}
),
renamed as (
    select
        cohort_month,
        observation_month,
        month_offset,
        amount_disbursed_m_kes,
        amount_repaid_m_kes,
        npl_amount_m_kes,
        active_loans_count
    from source
)
select * from renamed
