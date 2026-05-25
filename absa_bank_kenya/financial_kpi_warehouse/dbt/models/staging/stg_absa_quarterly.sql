with source as (
    select * from {{ source('absa_raw', 'raw_absa_financials') }}
),
renamed as (
    select
        indicator,
        year,
        value_m_kes,
        reported_date
    from source
)
select * from renamed
