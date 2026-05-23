with source as (
    select * from {{ source('absa_warehouse', 'raw_quarterly_data') }}
),

renamed as (
    select
        metric_name,
        period,
        value as metric_value,
        cast(extracted_at as timestamp) as extracted_at
    from source
)

select * from renamed
