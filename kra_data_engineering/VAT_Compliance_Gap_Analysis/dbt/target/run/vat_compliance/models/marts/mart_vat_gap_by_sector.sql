
  
    

  create  table "kra_warehouse"."public"."mart_vat_gap_by_sector__dbt_tmp"
  
  
    as
  
  (
    with staging as (
    select * from "kra_warehouse"."public"."stg_vat_compliance"
),
marts as (
    select
        sector,
        year,
        sector_gdp_m_kes,
        theoretical_vat_m_kes,
        actual_vat_m_kes,
        vat_gap_m_kes,
        c_efficiency_ratio,
        lag(c_efficiency_ratio) over (partition by sector order by year) as prev_year_efficiency
    from staging
)
select * from marts
  );
  