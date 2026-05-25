
  
    

  create  table "equitel_analytics"."public"."mart_adoption_curve__dbt_tmp"
  
  
    as
  
  (
    with transactions as (
    select * from "equitel_analytics"."public"."stg_eazzypay"
),
adoption as (
    select
        period,
        transaction_count,
        transaction_volume,
        lag(transaction_count) over (order by period) as prev_month_count,
        (transaction_count - lag(transaction_count) over (order by period))::float / nullif(lag(transaction_count) over (order by period), 0) * 100 as growth_rate
    from transactions
)
select * from adoption
  );
  