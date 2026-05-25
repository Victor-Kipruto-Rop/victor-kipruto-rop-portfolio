with staging as (
    select * from "pan_africa_platform"."public"."stg_subsidiaries"
),
consolidation as (
    select
        period,
        sum(profit_usd) as total_profit_usd,
        sum(profit_kes) as total_profit_kes,
        count(distinct subsidiary) as subsidiary_count
    from staging
    group by 1
)
select * from consolidation