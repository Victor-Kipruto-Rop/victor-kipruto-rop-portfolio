
  create view "pan_africa_platform"."public"."stg_customers__dbt_tmp"
    
    
  as (
    with source as (
    select * from "pan_africa_platform"."public"."customer_master"
),
renamed as (
    select
        customer_id,
        full_name,
        gender,
        age,
        customer_segment,
        subsidiary_name,
        country,
        account_type,
        account_status,
        account_balance_usd,
        loan_status,
        loan_amount_usd,
        credit_score_bucket,
        digital_engagement_score,
        nps_category
    from source
)
select * from renamed
  );