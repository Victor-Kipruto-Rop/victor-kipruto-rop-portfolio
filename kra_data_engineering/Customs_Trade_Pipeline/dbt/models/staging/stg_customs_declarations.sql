with source as (
    select * from {{ source('customs_raw', 'raw_customs_declarations') }}
),
renamed as (
    select
        declaration_id,
        cast(date as date) as declaration_date,
        cast(extract(year from cast(date as date)) as integer) as year,
        hs_code::varchar as hs_code,
        origin_country,
        destination_country,
        0.0 as volume_tons,
        cast(declared_value_kes as numeric) / 1000000.0 as declared_value_m_kes,
        cast(duty_paid_kes as numeric) / 1000000.0 as duty_collected_m_kes,
        has_rules_of_origin_cert,
        0 as risk_score
    from source
)
select * from renamed