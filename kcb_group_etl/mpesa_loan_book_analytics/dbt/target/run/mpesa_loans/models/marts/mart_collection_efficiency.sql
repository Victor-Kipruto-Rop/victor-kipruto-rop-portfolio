
  
    

  create  table "kcb_mpesa"."public"."mart_collection_efficiency__dbt_tmp"
  
  
    as
  
  (
    with staging as (
    select * from "kcb_mpesa"."public"."stg_mpesa_loans"
),
efficiency as (
    select
        cohort_month,
        observation_month,
        month_offset,
        amount_repaid_m_kes,
        amount_disbursed_m_kes,
        (amount_repaid_m_kes / nullif(amount_disbursed_m_kes, 0)) * 100 as repayment_rate_percent
    from staging
)
select * from efficiency
  );
  