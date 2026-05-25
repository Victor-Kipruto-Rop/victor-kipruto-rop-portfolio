with transactions as (
    select * from "absa_open_banking"."public"."stg_transactions"
),
daily_activity as (
    select
        account_id,
        date_trunc('day', transaction_date) as activity_date,
        count(*) as transaction_count,
        sum(amount) as total_volume
    from transactions
    group by 1, 2
)
select * from daily_activity