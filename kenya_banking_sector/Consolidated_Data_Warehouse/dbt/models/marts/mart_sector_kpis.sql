with staging as (
    select * from {{ ref('stg_cbk_returns') }}
),
pivoted as (
    select
        bank_id,
        year,
        max(case when return_code = 'A1' then value end) as total_assets,
        max(case when return_code = 'D1' then value end) as total_deposits,
        max(case when return_code = 'L1' then value end) as net_loans,
        max(case when return_code = 'P7' then value end) as net_profit,
        max(case when return_code = 'R1' then value end) as npl_ratio,
        max(case when return_code = 'C1' then value end) as capital_adequacy_ratio
    from staging
    group by 1, 2
),
calculated as (
    select
        p.*,
        b.bank_name,
        b.tier,
        (net_profit / nullif(total_assets, 0)) * 100 as roa,
        (net_loans / nullif(total_deposits, 0)) * 100 as loan_to_deposit_ratio
    from pivoted p
    left join {{ ref('bank_registry') }} b on p.bank_id = b.bank_id
)
select * from calculated
