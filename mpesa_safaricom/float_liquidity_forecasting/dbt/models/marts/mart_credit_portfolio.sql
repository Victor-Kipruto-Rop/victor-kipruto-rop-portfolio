/*
dbt mart model for Fuliza credit portfolio analysis

Provides portfolio-level credit risk metrics and performance analysis
for credit decisioning and portfolio management.

Grain: One row per customer per month
*/

with customer_monthly_metrics as (
    select
        date_trunc('month', transaction_date) as month_date,
        customer_phone,
        
        count(distinct transaction_id) as credit_count,
        sum(credit_amount) as total_credit_issued,
        sum(interest_charged) as total_interest_collected,
        avg(credit_amount) as avg_credit_size,
        max(credit_amount) as max_credit_size,
        
        sum(case when credit_size_category = 'large' then 1 else 0 end) as large_credit_count,
        sum(case when credit_size_category = 'medium' then 1 else 0 end) as medium_credit_count,
        sum(case when credit_size_category = 'small' then 1 else 0 end) as small_credit_count,
        
        max(customer_rating) as customer_rating,
        max(previous_credit_count) as credit_history_count,
        max(user_segment) as user_segment,
        
        count(distinct day_of_week) as active_days_in_month
        
    from {{ ref('stg_fuliza_transactions') }}
    
    group by
        date_trunc('month', transaction_date),
        customer_phone
)

select
    month_date,
    customer_phone,
    
    -- Volume metrics
    credit_count,
    total_credit_issued,
    total_interest_collected,
    round(avg_credit_size, 2) as avg_credit_size,
    max_credit_size,
    
    -- Credit mix
    large_credit_count,
    medium_credit_count,
    small_credit_count,
    round(
        100.0 * large_credit_count / (large_credit_count + medium_credit_count + small_credit_count),
        2
    ) as pct_large_credits,
    
    -- Customer metrics
    customer_rating,
    credit_history_count,
    user_segment,
    active_days_in_month,
    
    -- Risk scoring
    case
        when customer_rating >= 4 and credit_history_count > 10 then 'low'
        when customer_rating >= 3 and credit_history_count > 5 then 'medium'
        else 'high'
    end as risk_category,
    
    -- Calculated metrics
    round(total_interest_collected / nullif(total_credit_issued, 0), 4) as effective_interest_rate,
    round(active_days_in_month / 30.0, 2) as active_days_ratio,
    
    -- Metadata
    current_timestamp as created_at
    
from customer_monthly_metrics

order by
    month_date desc,
    total_credit_issued desc
