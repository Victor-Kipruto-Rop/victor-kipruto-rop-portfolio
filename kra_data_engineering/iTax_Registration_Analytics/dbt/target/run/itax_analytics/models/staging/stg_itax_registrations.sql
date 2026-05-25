
  create view "kra_warehouse"."public"."stg_itax_registrations__dbt_tmp"
    
    
  as (
    with source as (
    select * from "kra_warehouse"."public"."raw_itax_registrations"
),
renamed as (
    select
        pin,
        registration_date::date as registration_date,
        county,
        sector,
        is_active
    from source
)
select * from renamed
  );