with local_customs as (
    select * from {{ ref('mart_duty_collection') }}
),
benchmarks as (
    select * from {{ ref('stg_comtrade') }}
),
marts as (
    select
        l.year,
        sum(l.total_value_m_kes) as total_imports_value,
        sum(b.declared_value_m_kes) as global_export_benchmark_value,
        -- Trade balance logic
        (sum(l.total_value_m_kes) - sum(b.declared_value_m_kes)) as trade_discrepancy
    from local_customs l
    left join benchmarks b on l.hs_code = b.hs_code and l.year = b.year
    group by 1
)
select * from marts
