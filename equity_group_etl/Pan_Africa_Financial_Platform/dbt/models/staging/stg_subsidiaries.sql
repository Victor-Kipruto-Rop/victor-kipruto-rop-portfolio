with source as (
    select * from {{ source('pan_africa_raw', 'raw_subsidiary_financials') }}
),
renamed as (
    select
        subsidiary,
        period,
        currency,
        net_profit as profit_local,
        total_assets as assets_local,
        profit_usd,
        profit_kes
    from source
)
select * from renamed
