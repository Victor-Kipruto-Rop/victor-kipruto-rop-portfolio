with subscribers as (
    select * from "equitel_analytics"."public"."stg_equitel"
),
transactions as (
    select * from "equitel_analytics"."public"."stg_eazzypay"
),
joined as (
    select
        s.period,
        s.subscribers,
        t.transaction_volume,
        t.transaction_count
    from subscribers s
    left join transactions t on s.period = t.period
),
calculated as (
    select
        period,
        subscribers,
        transaction_volume,
        (transaction_volume / nullif(subscribers, 0)) as arpu_kes
    from joined
)
select * from calculated