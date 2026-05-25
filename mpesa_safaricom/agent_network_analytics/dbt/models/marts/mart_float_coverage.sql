{{
  config(
    materialized = 'table',
    tags = ['mart', 'float']
  )
}}

\-- mart_float_coverage.sql
\-- Float-balance coverage metrics at ward level:
\--   • avg_float              mean float balance across agents in the ward
\--   • float_below_threshold  # agents whose float < FLOAT_ALERT_THRESHOLD KES
\--   • float_coverage_ratio   tokens float / tokenised-transaction value

WITH ward_enriched AS (
    SELECT
        w.ward_code
      , w.ward_name
      , w.county
      , w.geom
      , COUNT(a.agent_id)                                 AS agent_count
      , COALESCE(SUM(a.float_balance), 0.0)               AS total_float
      , AVG(a.float_balance)                              AS avg_float
      , SUM(CASE
               WHEN a.float_balance < {{ var('FLOAT_ALERT_THRESHOLD', 50000) }}
               THEN 1
               ELSE 0
            END)                                          AS float_below_threshold
      , COALESCE(SUM(a.float_balance), 0.0)
        / NULLIF(SUM(a.total_transaction_amount), 0)      AS float_coverage_ratio
    FROM {{ ref('raw_wards') }} w
    LEFT JOIN {{ ref('raw_agents') }} a
      ON (w.geom IS NOT NULL
          AND a.geom IS NOT NULL
          AND ST_Contains(w.geom, a.geom))
      OR (w.geom IS NULL
          AND lower(coalesce(a.ward, '')) = lower(coalesce(w.ward_name, '')))
    GROUP BY w.ward_code, w.ward_name, w.county, w.geom
)

SELECT
    ward_code
  , ward_name
  , county
  , agent_count
  , ROUND(total_float::numeric, 2)        AS total_float
  , ROUND(avg_float::numeric, 2)          AS avg_float
  , float_below_threshold
  , ROUND(float_coverage_ratio::numeric, 4) AS float_coverage_ratio
  , geom
FROM ward_enriched
