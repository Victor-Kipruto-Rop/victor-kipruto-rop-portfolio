with gdp as (
    select
        year,
        sum(gdp_current_prices_m_kes) as total_gdp_m_kes
    from {{ ref('stg_economic_survey') }}
    group by 1
),
revenue as (
    select
        year,
        sum(actual_revenue_m_kes) as total_revenue_m_kes
    from {{ ref('stg_revenue_monthly') }}
    group by 1
),
joined as (
    select
        g.year,
        g.total_gdp_m_kes,
        r.total_revenue_m_kes,
        (r.total_revenue_m_kes / nullif(g.total_gdp_m_kes, 0)) * 100 as tax_to_gdp_ratio_percent
    from gdp g
    left join revenue r on g.year = r.year
)
select * from joined
