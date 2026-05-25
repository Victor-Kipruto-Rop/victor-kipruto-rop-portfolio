with staging as (
    select * from {{ ref('stg_economic_survey') }}
)
select
    year,
    industry,
    gdp_current_prices_m_kes,
    growth_rate_percent
from staging
where year >= 2021
order by year desc, gdp_current_prices_m_kes desc
