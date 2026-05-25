with source as (
    select * from {{ source('customs_raw', 'raw_customs_trade_data') }}
),
renamed as (
    select
        cast(cmdcode as varchar) as hs_code,
        cmddesc as commodity,
        partnerdesc as origin_country,
        cast(refyear as integer) as year,
        cast(netwgt as numeric) / 1000.0 as volume_tons,
        cast(primaryvalue as numeric) / 1000000.0 as declared_value_m_kes,
        0.0 as duty_collected_m_kes, -- Not in raw data
        0 as risk_score -- Not in raw data
    from source
)
select * from renamed
