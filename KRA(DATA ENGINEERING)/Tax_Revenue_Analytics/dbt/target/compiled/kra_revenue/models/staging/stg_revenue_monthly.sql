with source as (
    select * from "kra_warehouse"."public"."raw_kra_revenue"
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