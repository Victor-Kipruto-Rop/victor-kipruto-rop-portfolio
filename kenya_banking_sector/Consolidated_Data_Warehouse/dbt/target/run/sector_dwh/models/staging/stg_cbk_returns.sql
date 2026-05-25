
  create view "sector_dwh"."public"."stg_cbk_returns__dbt_tmp"
    
    
  as (
    with source as (
    select * from "sector_dwh"."public"."raw_cbk_returns"
),
renamed as (
    select
        bank_id,
        year,
        return_code,
        value,
        reported_date
    from source
)
select * from renamed
  );