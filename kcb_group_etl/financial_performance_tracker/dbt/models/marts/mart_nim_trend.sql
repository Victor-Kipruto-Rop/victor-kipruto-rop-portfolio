with staging as (
    select * from {{ ref('stg_kcb_financials') }}
),
nim_calc as (
    select
        subsidiary,
        year,
        net_interest_income_m_kes,
        total_assets_m_kes,
        (net_interest_income_m_kes / nullif(total_assets_m_kes, 0)) * 100 as nim_percent
    from staging
)
select * from nim_calc
