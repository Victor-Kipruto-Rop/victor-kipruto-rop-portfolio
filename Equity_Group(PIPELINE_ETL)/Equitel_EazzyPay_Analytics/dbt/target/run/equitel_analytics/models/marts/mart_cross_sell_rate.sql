
  
    

  create  table "equitel_analytics"."public"."mart_cross_sell_rate__dbt_tmp"
  
  
    as
  
  (
    with subscribers as (
    select * from "equitel_analytics"."public"."stg_equitel"
),
transactions as (
    select * from "equitel_analytics"."public"."stg_eazzypay"
),
joined as (
    select
        s.period,
        s.subscribers as total_base,
        t.insurance_subscribers,
        t.investment_subscribers
    from subscribers s
    left join transactions t on s.period = t.period
),
rates as (
    select
        period,
        total_base,
        insurance_subscribers,
        investment_subscribers,
        (insurance_subscribers::float / nullif(total_base, 0)) * 100 as insurance_cross_sell_rate,
        (investment_subscribers::float / nullif(total_base, 0)) * 100 as investment_cross_sell_rate
    from joined
)
select * from rates
  );
  