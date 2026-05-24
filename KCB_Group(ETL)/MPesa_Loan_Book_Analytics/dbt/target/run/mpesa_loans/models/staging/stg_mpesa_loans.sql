
  create view "kcb_mpesa"."public"."stg_mpesa_loans__dbt_tmp"
    
    
  as (
    with source as (
    select * from "kcb_mpesa"."public"."raw_kcb_mpesa_loans"
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
  );