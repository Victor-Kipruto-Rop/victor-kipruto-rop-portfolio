with staging as (
    select * from {{ ref('stg_equity_transactions') }}
),
channel_metrics as (
    select
        channel,
        count(*) as total_transactions,
        sum(amount_kes) as total_volume_kes,
        avg(amount_kes) as avg_transaction_value
    from staging
    group by 1
)
select * from channel_metrics
