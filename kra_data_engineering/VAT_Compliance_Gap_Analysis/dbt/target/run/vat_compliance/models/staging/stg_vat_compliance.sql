
  create view "kra_warehouse"."public"."stg_vat_compliance__dbt_tmp"
    
    
  as (
    with source as (
    select * from "kra_warehouse"."public"."raw_vat_compliance"
),
renamed as (
    select
        sector,
        year,
        sector_gdp_m_kes,
        theoretical_vat_m_kes,
        actual_vat_m_kes,
        vat_gap_m_kes,
        c_efficiency_ratio
    from source
)
select * from renamed
  );