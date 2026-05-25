with staging as (
    select * from "kra_warehouse"."public"."stg_itax_registrations"
),
marts as (
    select
        county,
        sector,
        date_trunc('month', registration_date) as registration_month,
        count(pin) as new_registrations,
        sum(case when is_active then 1 else 0 end) as active_registrations
    from staging
    group by 1, 2, 3
)
select * from marts