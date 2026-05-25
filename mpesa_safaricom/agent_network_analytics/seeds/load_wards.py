"""
load_wards.py

Load seeds/kenya_wards.csv into PostGIS as table 'wards'. If no geometry, attempt to construct ward geometries
by aggregating agent points (convex hull). Safe and idempotent.
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

DB_URL = os.getenv('MPESA_DATABASE_URL', 'postgresql://mpesa:mpesa_pass@localhost:5433/mpesa')
SEED = Path(__file__).resolve().parents[1] / 'seeds' / 'kenya_wards.csv'


def load():
    if not SEED.exists():
        print('Seed file not found:', SEED)
        return
    df = pd.read_csv(SEED)
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS postgis;'))
        conn.execute(text('CREATE TABLE IF NOT EXISTS wards (ward_code TEXT PRIMARY KEY, county TEXT, constituency TEXT, ward_name TEXT);'))
        # upsert rows
        for _, r in df.iterrows():
            conn.execute(text('INSERT INTO wards (ward_code, county, constituency, ward_name) VALUES (:wc, :county, :const, :wname) ON CONFLICT (ward_code) DO UPDATE SET county=EXCLUDED.county, constituency=EXCLUDED.constituency, ward_name=EXCLUDED.ward_name;'),
                         {'wc': str(r.get('ward_code')), 'county': r.get('county'), 'const': r.get('constituency'), 'wname': r.get('ward_name')})
        # ensure geom column
        conn.execute(text('ALTER TABLE wards ADD COLUMN IF NOT EXISTS geom geometry(MultiPolygon,4326);'))
        # build geometries from agent points where possible
        # Use case-insensitive matching on ward_name
        # Try flexible matching: match by county and ward name equality or substring matches
        conn.execute(text("""
            UPDATE wards w SET geom = sub.hull FROM (
                SELECT w2.ward_code, ST_Multi(ST_ConvexHull(ST_Collect(a.geom))) AS hull
                FROM wards w2
                JOIN agents a ON a.geom IS NOT NULL
                  AND lower(coalesce(a.county,'')) = lower(coalesce(w2.county,''))
                  AND (
                    lower(coalesce(a.ward,'')) = lower(coalesce(w2.ward_name,''))
                    OR position(lower(coalesce(w2.ward_name,'')) IN lower(coalesce(a.ward,''))) > 0
                    OR position(lower(coalesce(a.ward,'')) IN lower(coalesce(w2.ward_name,''))) > 0
                  )
                GROUP BY w2.ward_code
            ) AS sub
            WHERE w.ward_code = sub.ward_code AND sub.hull IS NOT NULL;
        """))
    print('Loaded wards and computed geometries where possible')


if __name__ == '__main__':
    load()
