
  
    

  create  table "kcb_mpesa"."public"."mart_loan_cohorts__dbt_tmp"
  
  
    as
  
  (
    with staging as (
    select * from "kcb_mpesa"."public"."stg_mpesa_loans"
),
cohorts as (
    select
        cohort_month,
        sum(amount_disbursed_m_kes) as total_disbursed,
        sum(active_loans_count) as total_active_loans
    from staging
    group by cohort_month
)
select * from cohorts
  );
  