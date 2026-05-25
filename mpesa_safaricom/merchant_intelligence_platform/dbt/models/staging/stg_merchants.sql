with source as (
    select * from {{ source('merchant_raw', 'raw_merchants') }}
),
renamed as (
    select
        merchant_id,
        name as merchant_name,
        category,
        county,
        cast(daily_transactions as integer) as daily_transactions,
        cast(avg_ticket_size_kes as numeric) as avg_ticket_size_kes,
        cast(monthly_volume_kes as numeric) as monthly_volume_kes,
        cast(churn_risk_score as float) as churn_risk_score
    from source
)
select * from renamed
