with source as (
    select * from {{ source('sector_raw', 'raw_cbk_returns') }}
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
