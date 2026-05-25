with remittances as (
    select * from {{ ref('stg_remittances') }}
),
fees as (
    select
        sender_country,
        avg(transfer_fee_usd / nullif(amount_usd, 0)) * 100 as avg_fee_percentage,
        min(transfer_fee_usd / nullif(amount_usd, 0)) * 100 as min_fee_percentage,
        max(transfer_fee_usd / nullif(amount_usd, 0)) * 100 as max_fee_percentage
    from remittances
    group by 1
)
select * from fees
