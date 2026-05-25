
  create view "kcb_financials"."public"."stg_kcb_financials__dbt_tmp"
    
    
  as (
    with source as (
    select * from "kcb_financials"."public"."raw_kcb_financials"
),
renamed as (
    select
        subsidiary,
        year,
        net_profit_m_kes,
        total_assets_m_kes,
        interest_income_m_kes,
        interest_expense_m_kes,
        net_interest_income_m_kes,
        operating_expenses_m_kes,
        shareholders_equity_m_kes,
        npl_ratio_percent,
        customer_count
    from source
)
select * from renamed
  );