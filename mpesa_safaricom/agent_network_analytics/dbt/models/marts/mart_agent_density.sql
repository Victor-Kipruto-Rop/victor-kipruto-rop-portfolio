{{
  config(
    materialized = 'table',
    tags = ['mart', 'density']
  )
}}

\-- mart_agent_density.sql
\-- Ward-level agent density metrics: count, density per km², and
\-- average transaction volume.  Falls back gracefully when ward
\-- geometry is absent by joining on ward name only.

WITH ward_enriched AS (
    SELECT
        w.ward_code
      , w.ward_name
      , w.county
      , w.geom
      , COUNT(a.agent_id)                            AS agent_count
      , COALESCE(SUM(a.transactions), 0)             AS total_transactions
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
  , total_transactions
  , CASE
      WHEN ST_Area(geom::geography) > 0
      THEN agent_count
           / (ST_Area(geom::geography) / 1_000_000.0)   -- km²
      ELSE NULL
    END                                           AS density_per_km2
  , CASE
      WHEN agent_count > 0
      THEN ROUND(total_transactions::numeric / agent_count, 2)
      ELSE 0
    END                                           AS avg_transactions_per_agent
  , geom
FROM ward_enriched
