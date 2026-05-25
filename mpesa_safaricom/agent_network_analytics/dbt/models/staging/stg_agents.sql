with source as (
    select * from {{ source('agent_raw', 'raw_agents') }}
),
renamed as (
    select
        agent_id,
        county,
        latitude,
        longitude,
        cast(float_balance as numeric) as float_balance,
        txns_today,
        cast(last_restock_at as timestamp) as last_restock_at,
        is_active
    from source
)
select * from renamed
