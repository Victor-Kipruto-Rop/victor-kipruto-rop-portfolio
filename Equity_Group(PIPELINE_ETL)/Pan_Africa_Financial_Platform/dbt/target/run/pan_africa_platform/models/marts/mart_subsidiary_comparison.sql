
  
    

  create  table "pan_africa_platform"."public"."mart_subsidiary_comparison__dbt_tmp"
  
  
    as
  
  (
    with staging as (
    select * from "pan_africa_platform"."public"."stg_subsidiaries"
),
comparison as (
    select
        subsidiary,
        period,
        profit_usd,
        profit_kes,
        (profit_usd / sum(profit_usd) over (partition by period)) * 100 as contribution_percentage
    from staging
)
select * from comparison
  );
  