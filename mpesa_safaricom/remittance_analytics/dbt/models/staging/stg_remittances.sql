with source as (
    select * from {{ source('remittance_raw', 'raw_remittances') }}
),
renamed as (
    select
        transfer_id,
        sender_country,
        receiver_country,
        cast(amount_usd as numeric) as amount_usd,
        cast(transfer_fee_usd as numeric) as transfer_fee_usd,
        cast(exchange_rate as numeric) as exchange_rate,
        cast(transfer_date as date) as transfer_date,
        (amount_usd * exchange_rate) as amount_kes
    from source
)
select * from renamed
