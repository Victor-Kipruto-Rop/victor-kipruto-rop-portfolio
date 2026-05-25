with merchants as (
    select * from {{ ref('stg_merchants') }}
),
density as (
    select
        county,
        category,
        count(*) as merchant_count,
        sum(monthly_volume_kes) as total_county_volume
    from merchants
    group by 1, 2
)
select * from density
