with remittances as (
    select * from {{ ref('stg_remittances') }}
),
corridors as (
    select
        sender_country,
        count(*) as total_transfers,
        sum(amount_usd) as total_usd_volume,
        avg(amount_usd) as avg_transfer_size_usd
    from remittances
    group by 1
)
select * from corridors
order by total_usd_volume desc
