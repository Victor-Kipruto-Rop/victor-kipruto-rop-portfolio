/*
dbt staging model for M-Pesa Fuliza credit transactions

Standardizes credit advance, repayment, and interest data from Safaricom.
Grain: One row per credit transaction
*/

with source_fuliza as (
    select
        cast(transaction_id as string) as transaction_id,
        cast(customer_phone as string) as customer_phone,
        cast(credit_amount as numeric(10, 2)) as credit_amount,
        cast(interest_charged as numeric(10, 2)) as interest_charged,
        cast(transaction_date as date) as transaction_date,
        cast(transaction_time as timestamp) as transaction_time,
        cast(customer_rating as integer) as customer_rating,
        cast(previous_credit_count as integer) as previous_credit_count,
        cast(days_since_last_credit as integer) as days_since_last_credit,
        cast(_loaded_at as timestamp) as loaded_at
        
    from {{ source('safaricom', 'fuliza_transactions_raw') }}
    
    where
        -- Data quality
        transaction_id is not null
        and customer_phone like '254%'
        and credit_amount > 0
        and transaction_date >= date_add(current_date, interval -365 day)
)

select
    *,
    -- Calculate derived metrics
    case
        when credit_amount >= 5000 then 'large'
        when credit_amount >= 1000 then 'medium'
        else 'small'
    end as credit_size_category,
    
    case
        when interest_charged / credit_amount > 0.05 then 'high'
        when interest_charged / credit_amount > 0.01 then 'standard'
        else 'low'
    end as interest_rate_category,
    
    case
        when previous_credit_count = 0 then 'new_user'
        when previous_credit_count <= 5 then 'active_user'
        else 'power_user'
    end as user_segment,
    
    extract(dayofweek from transaction_date) as day_of_week,
    extract(month from transaction_date) as month,
    extract(year from transaction_date) as year,
    
    current_timestamp as processed_at
    
from source_fuliza
