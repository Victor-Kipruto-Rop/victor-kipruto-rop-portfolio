
  create view "equitel_analytics"."public"."stg_equitel__dbt_tmp"
    
    
  as (
    with source as (
    select * from "equitel_analytics"."public"."raw_equitel_subscribers"
),
renamed as (
    select
        period,
        subscribers,
        operator
    from source
)
select * from renamed
  );