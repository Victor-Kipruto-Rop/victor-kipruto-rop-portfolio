
  
    

  create  table "kra_warehouse"."public"."mart_revenue_by_tax_head__dbt_tmp"
  
  
    as
  
  (
    with monthly as (
    select * from "kra_warehouse"."public"."stg_revenue_monthly"
),
marts as (
    select
        tax_head,
        year,
        sum(actual_revenue_m_kes) as annual_actual_revenue,
        sum(target_revenue_m_kes) as annual_target_revenue,
        (sum(actual_revenue_m_kes) / nullif(sum(target_revenue_m_kes), 0)) * 100 as performance_percent
    from monthly
    group by 1, 2
)
select * from marts
  );
  