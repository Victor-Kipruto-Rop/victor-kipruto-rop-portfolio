with staging as (
    select * from {{ ref('stg_equity_transactions') }}
),
county_metrics as (
    select
        county,
        count(*) as transaction_count,
        sum(amount_kes) as volume_kes
    from staging
    group by 1
)
select * from county_metrics
