with source as (
    select * from {{ source('absa_open_banking', 'raw_transactions') }}
),
renamed as (
    select
        transaction_id,
        account_id,
        amount,
        currency,
        description,
        cast(transaction_date as timestamp) as transaction_date,
        status
    from source
)
select * from renamed
