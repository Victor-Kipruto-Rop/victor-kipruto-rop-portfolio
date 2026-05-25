with source as (
    select * from {{ ref('subsidiaries') }}
)
select * from source
