with source as (
    select * from {{ source('kra_raw', 'raw_kra_revenue') }}
),
renamed as (
    select
        tax_head,
        year,
        month,
        actual_revenue_m_kes,
        target_revenue_m_kes,
        reported_date
    from source
)
select * from renamed
