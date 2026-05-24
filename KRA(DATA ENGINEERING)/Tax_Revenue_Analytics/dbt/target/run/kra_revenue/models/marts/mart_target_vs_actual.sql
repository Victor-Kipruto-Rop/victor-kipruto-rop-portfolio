
  
    

  create  table "kra_warehouse"."public"."mart_target_vs_actual__dbt_tmp"
  
  
    as
  
  (
    with monthly as (
    select * from "kra_warehouse"."public"."stg_revenue_monthly"
),
summary as (
    select
        year,
        month,
        sum(actual_revenue_m_kes) as total_actual,
        sum(target_revenue_m_kes) as total_target,
        (sum(actual_revenue_m_kes) / nullif(sum(target_revenue_m_kes), 0)) * 100 as monthly_performance
    from monthly
    group by 1, 2
)
select * from summary
  );
  