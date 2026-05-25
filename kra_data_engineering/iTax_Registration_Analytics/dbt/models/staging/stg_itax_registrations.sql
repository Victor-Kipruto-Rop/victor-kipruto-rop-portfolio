with source as (
    select * from {{ source('itax_raw', 'raw_itax_registrations') }}
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
