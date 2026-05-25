
  
    

  create  table "kcb_financials"."public"."mart_npl_ratio__dbt_tmp"
  
  
    as
  
  (
    with staging as (
    select * from "kcb_financials"."public"."stg_kcb_financials"
),
asset_quality as (
    select
        subsidiary,
        year,
        npl_ratio_percent,
        total_assets_m_kes,
        (npl_ratio_percent / 100) * total_assets_m_kes as npl_amount_m_kes
    from staging
)
select * from asset_quality
  );
  