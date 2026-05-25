with agents as (
    select * from {{ ref('stg_agents') }}
),
at_risk as (
    select
        *,
        case 
            when float_balance < 5000 then 'Critical'
            when float_balance < 20000 then 'Low'
            else 'Healthy'
        end as risk_level
    from agents
    where is_active = true
)
select * from at_risk
where risk_level in ('Critical', 'Low')
