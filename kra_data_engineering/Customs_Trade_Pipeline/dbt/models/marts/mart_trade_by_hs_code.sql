with customs as (
    select * from {{ ref('mart_duty_collection') }}
),
marts as (
    select
        hs_code,
        commodity_description,
        year,
        sum(total_volume_tons) as annual_volume,
        sum(total_value_m_kes) as annual_value,
        sum(total_duty_m_kes) as annual_duty
    from customs
    group by 1, 2, 3
)
select * from marts
