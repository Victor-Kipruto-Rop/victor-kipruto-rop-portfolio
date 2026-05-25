with merchants as (
    select * from {{ ref('stg_merchants') }}
),
segments as (
    select
        *,
        case 
            when monthly_volume_kes > 10000000 then 'Enterprise'
            when monthly_volume_kes > 1000000 then 'Key Account'
            else 'SME'
        end as merchant_segment,
        case
            when churn_risk_score > 0.7 then 'High Risk'
            when churn_risk_score > 0.4 then 'Medium Risk'
            else 'Loyal'
        end as engagement_level
    from merchants
)
select * from segments
