
  create view "pan_africa_platform"."public"."stg_subsidiary_meta__dbt_tmp"
    
    
  as (
    with source as (
    select * from "pan_africa_platform"."public"."subsidiaries"
)
select * from source
  );