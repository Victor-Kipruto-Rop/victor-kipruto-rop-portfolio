with source as (
    select * from {{ source('equitel_raw', 'raw_equitel_subscribers') }}
),
renamed as (
    select
        period,
        subscribers,
        operator
    from source
)
select * from renamed
