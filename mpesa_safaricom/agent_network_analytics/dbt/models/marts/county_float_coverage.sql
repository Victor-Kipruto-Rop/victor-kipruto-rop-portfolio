with agents as (
    select * from {{ ref('stg_agents') }}
),
county_stats as (
    select
        county,
        count(*) as total_agents,
        sum(float_balance) as total_float_kes,
        avg(float_balance) as avg_float_kes,
        sum(txns_today) as total_daily_txns
    from agents
    where is_active = true
    group by 1
)
select * from county_stats
