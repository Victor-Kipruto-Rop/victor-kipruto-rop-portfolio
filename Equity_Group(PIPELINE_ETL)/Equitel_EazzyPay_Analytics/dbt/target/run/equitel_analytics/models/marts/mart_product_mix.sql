
  
    

  create  table "equitel_analytics"."public"."mart_product_mix__dbt_tmp"
  
  
    as
  
  (
    with subscribers as (
    select * from "equitel_analytics"."public"."stg_equitel"
),
transactions as (
    select * from "equitel_analytics"."public"."stg_eazzypay"
),
mix as (
    select
        s.period,
        s.subscribers as total_base,
        t.insurance_subscribers,
        t.investment_subscribers,
        (s.subscribers - t.insurance_subscribers - t.investment_subscribers) as pure_mobile_users
    from subscribers s
    left join transactions t on s.period = t.period
)
select * from mix
  );
  