with source as (
    select * from {{ source('equity_raw', 'raw_equity_kenya_transactions') }}
),
renamed as (
    select
        transaction_id,
        cast(timestamp as timestamp) as transaction_timestamp,
        channel,
        category,
        cast(amount_kes as numeric) as amount_kes,
        county,
        cast(is_fraudulent as boolean) as is_fraudulent
    from source
)
select * from renamed
