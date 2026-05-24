
  create view "equitel_analytics"."public"."stg_eazzypay__dbt_tmp"
    
    
  as (
    with source as (
    select * from "equitel_analytics"."public"."raw_eazzypay_transactions"
),
renamed as (
    select
        period,
        transaction_volume,
        transaction_count,
        insurance_subscribers,
        investment_subscribers,
        product
    from source
)
select * from renamed
  );