
  
    

  create  table "kcb_financials"."public"."mart_nim_trend__dbt_tmp"
  
  
    as
  
  (
    with staging as (
    select * from "kcb_financials"."public"."stg_kcb_financials"
),
nim_calc as (
    select
        subsidiary,
        year,
        net_interest_income_m_kes,
        total_assets_m_kes,
        (net_interest_income_m_kes / nullif(total_assets_m_kes, 0)) * 100 as nim_percent
    from staging
)
select * from nim_calc
  );
  