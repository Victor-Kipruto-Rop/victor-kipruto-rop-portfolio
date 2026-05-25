with source as (
    select * from "kra_warehouse"."public"."raw_economic_survey_gdp"
),
renamed as (
    select
        industry,
        cast(year as integer) as year,
        cast(gdp_current_prices_m_kes as numeric) as gdp_current_prices_m_kes,
        cast(growth_rate_percent as numeric) as growth_rate_percent
    from source
)
select * from renamed