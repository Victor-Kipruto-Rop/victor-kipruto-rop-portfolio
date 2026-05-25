{{
  config(
    materialized = 'view',
    tags = ['staging']
  )
}}

\--  stg_wards.sql
\--  Reads the ``wards`` seed table (loaded via ``dbt seed`` from
\--  ``seeds/kenya_wards.csv``) and enriches it with a geometry column
\--  built from the centroid of each ward's polygon (already present in
\--  the ``ward_agent_aggregates`` table once ingestion has run).

SELECT
    w.ward_code
  , w.ward_name
  , w.county
  , w.constituency
  , COALESCE(
        c.centroid_geom
      , ST_PointOnSurface(w.geom)
    )                                     AS geom
  , w.geom                                AS ward_polygon
FROM {{ ref('raw_wards') }} w

\-- The ward aggregate table carries a pre-computed centroid so we
\-- don't have to re-derive one from the seed geometry every time.
LEFT JOIN (
    SELECT DISTINCT ON (ward_code)
           ward_code
         , ST_Centroid(geom) AS centroid_geom
    FROM {{ ref('raw_ward_agent_aggregates') }}
    WHERE geom IS NOT NULL
) c ON c.ward_code = w.ward_code
