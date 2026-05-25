{{ config(
    materialized = 'view',
    tags = ['staging', 'agents']
) }}

with source_data as (
    select
        cast(agent_id as varchar) as agent_id,
        cast(agent_name as varchar) as agent_name,
        cast(region as varchar) as region,
        cast(float_balance as numeric(18, 2)) as float_balance,
        cast(status as varchar) as status,
        cast(activated_date as date) as activated_date,
        cast(last_transaction_date as date) as last_transaction_date,
        cast(created_at as timestamp) as created_at,
        cast(updated_at as timestamp) as updated_at
    from {{ source('raw', 'agent_data') }}
    where agent_id is not null
),

with_flags as (
    select
        *,
        case when float_balance < 0 then 1 else 0 end as is_negative_float,
        case when float_balance > 100000 then 1 else 0 end as is_high_float,
        case when last_transaction_date < current_date - interval '7' day then 1 else 0 end as is_inactive
    from source_data
)

select
    agent_id,
    agent_name,
    region,
    float_balance,
    status,
    activated_date,
    last_transaction_date,
    is_negative_float,
    is_high_float,
    is_inactive,
    current_timestamp as dbt_processed_at
from with_flags
where status in ('ACTIVE', 'INACTIVE')
