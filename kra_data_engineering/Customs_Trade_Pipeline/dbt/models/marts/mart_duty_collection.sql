with declarations as (
    select * from {{ ref('stg_customs_declarations') }}
),
hs_codes as (
    select * from {{ ref('hs_codes') }}
),
joined as (
    select
        d.hs_code,
        h.commodity_description,
        h.section_name as commodity_category,
        d.origin_country,
        d.year,
        sum(d.volume_tons) as total_volume_tons,
        sum(d.declared_value_m_kes) as total_value_m_kes,
        sum(d.duty_collected_m_kes) as total_duty_m_kes,
        avg(d.risk_score) as avg_risk_score
    from declarations d
    left join hs_codes h on d.hs_code = h.hs_code::varchar -- Added explicit cast
    group by 1, 2, 3, 4, 5
)
select * from joined
