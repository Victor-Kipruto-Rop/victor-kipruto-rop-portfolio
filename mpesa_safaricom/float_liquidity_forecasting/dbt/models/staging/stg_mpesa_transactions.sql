{{ config(
    materialized = 'view',
    tags = ['staging', 'raw']
) }}

with source_data as (
    select
        cast(transaction_date as date) as transaction_date,
        cast(transaction_id as varchar) as transaction_id,
        cast(sender_type as varchar) as sender_type,
        cast(receiver_type as varchar) as receiver_type,
        cast(transaction_amount as numeric(18, 2)) as transaction_amount,
        cast(transaction_count as integer) as transaction_count,
        cast(region as varchar) as region,
        cast(created_at as timestamp) as created_at,
        cast(updated_at as timestamp) as updated_at
    from {{ source('raw', 'mpesa_transactions') }}
    where transaction_date is not null
),

cleaned as (
    select
        *,
        case 
            when transaction_count = 0 then null 
            else transaction_amount / transaction_count 
        end as avg_transaction_value
    from source_data
)

select
    transaction_date,
    transaction_id,
    sender_type,
    receiver_type,
    transaction_amount,
    transaction_count,
    avg_transaction_value,
    region,
    created_at,
    updated_at
from cleaned
