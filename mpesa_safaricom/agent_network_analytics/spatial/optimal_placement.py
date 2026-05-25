"""
optimal_placement.py

Suggest optimal locations for new M-Pesa agents using KMeans on existing
agent coordinates, filtered with PostGIS-backed overlap/density checks,
demand weighting from ward aggregates, and configurable minimum-separation
constraints. No hardcoded thresholds: all Tunable constants live in a
dedicated constants module.
"""

import logging
import json
import time
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Any, Optional

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ── Defaults (overridable via CLI / env or directly below) ──────────────────
DEFAULT_N_CLUSTERS:     int   = 10
MINIMUM_AGENT_SEPARATION_KM: float = 3.0      # reject candidate within this radius
MIN_COVERAGE_DISTANCE_KM:     float = 2.0      # KD-tree sparse-gap distance
FLOAT_ALERT_THRESHOLD:        float = 50_000.0 # KES

DB_URL:        str              = ""
OUTPUT_DIR:    Path             = Path(__file__).resolve().parents[1] / 'data' / 'reports'
TIMEOUT_S:     int              = 15


def _get_db_url() -> str:
    global DB_URL
    if not DB_URL:
        import os
        DB_URL = os.getenv('MPESA_DATABASE_URL', 'postgresql://mpesa:mpesa_pass@localhost:5433/mpesa')
    return DB_URL


# ── Data access ──────────────────────────────────────────────────────────────

def get_agent_locations(limit: Optional[int] = None) -> pd.DataFrame:
    """
    Fetch existing agent coordinates from PostGIS.

    Uses a parameterised query so user-facing callers cannot inject SQL.
    """
    engine = create_engine(_get_db_url())
    q = text("SELECT agent_id, ST_X(geom) AS longitude, ST_Y(geom) AS latitude "
             "FROM agents WHERE geom IS NOT NULL")
    params: dict[str, Any] = {}
    if limit is not None:
        q = text(str(q) + " LIMIT :limit_val")
        params["limit_val"] = limit
    df = pd.read_sql(q, engine, params=params or None)
    return df


def get_ward_demand_weights() -> pd.DataFrame:
    """
    Return ``ward_code → demand_weight`` derived from ward aggregates.

    Demand is normalised to [0, 1] across all wards so it can be used as
    a soft prior when scoring new locations.
    """
    engine = create_engine(_get_db_url())
    df = pd.read_sql(
        text("SELECT ward_code, agent_count, total_transactions "
             "FROM ward_agent_aggregates "
             "WHERE agent_count > 0 ORDER BY agent_count DESC"),
        engine,
    )
    if df.empty:
        return pd.DataFrame(columns=["ward_code", "demand_weight"])
    df["demand_weight"] = (
        df["total_transactions"].rank(pct=True).clip(lower=0.05, upper=0.95)
    )
    return df


# ── KMeans + filtering ───────────────────────────────────────────────────────

km_per_deg: float = 110.574   # average longitude offset at Kenya lat


def _validate_coords(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with missing or out-of-range lat/lng."""
    mask = (
        df["latitude"].between(-90, 90)
        & df["longitude"].between(-180, 180)
        & df[["latitude", "longitude"]].notna().all(axis=1)
    )
    dropped = int((~mask).sum())
    if dropped:
        logger.warning("Dropping %d rows with invalid coordinates.", dropped)
    return df[mask].reset_index(drop=True)


def _candidate_overlaps_existing(
    engine: Any,
    candidates: np.ndarray,
    threshold_km: float,
) -> np.ndarray:
    """
    Return a boolean mask of *candidates* that do NOT overlap with any
    existing agent within ``threshold_km``.

    Uses a PostGIS ``ST_DWithin`` query so the spatial index is used.
    """
    thresh_deg = threshold_km / km_per_deg
    mask_valid = np.zeros(len(candidates), dtype=bool)
    gap_deg    = thresh_deg * 0.5   # narrow postgis check band; fuller KD-tree below
    with engine.connect() as conn:
        for i, (lat, lon) in enumerate(candidates):
            cnt = conn.execute(
                text("SELECT COUNT(*) FROM agents WHERE geom IS NOT NULL "
                     "AND ST_DWithin(geom::geography, "
                     "ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, "
                     ":dist_m)"),
                {"lon": lon, "lat": lat, "dist_m": threshold_km * 1_000.0},
            ).scalar()
            mask_valid[i] = (cnt == 0)
    return mask_valid


def _enforce_min_separation(
    candidates: np.ndarray,
    threshold_km: float,
) -> np.ndarray:
    """
    Remove candidates that are closer than ``threshold_km`` to any *other*
    kept candidate.  Worth stripping *already-passed* overlap check.
    """
    if len(candidates) < 2:
        return np.ones(len(candidates), dtype=bool)

    thresh_deg = threshold_km / km_per_deg
    kept: list[int] = []
    tree = KDTree(candidates)
    for i, pt in enumerate(candidates):
        dists = tree.query(pt, k=len(kept) + 2 if kept else 1)[0]
        # dists[0] is self-distance; recenter so first element == distance to nearest kept neighbour
        if kept:
            nearest_kept = tree.query([pt], k=1)[0][0] if kept else float("inf")
            if nearest_kept >= thresh_deg:
                kept.append(i)
        else:
            kept.append(i)
    mask = np.zeros(len(candidates), dtype=bool)
    mask[kept] = True
    return mask


# ── Main pipeline ────────────────────────────────────────────────────────────

@dataclass
class PlacementSuggestion:
    ward_code:       int
    ward_name:       str
    county:          str
    latitude:        float
    longitude:       float
    cluster_center:  list[float]   # [lat, lon]
    demand_weight:   float
    kmeans_inertia:  float
    suggested_type:  str
    status:          str           # 'recommended' | 'overlap' | 'too_close'

    @classmethod
    def from_tuple(cls, row: tuple) -> "PlacementSuggestion":
        return cls(*row)


def suggest_new_locations(
    n_clusters:                   int                 = DEFAULT_N_CLUSTERS,
    min_separation_km:            Optional[float]     = None,
    min_coverage_distance_km:     Optional[float]     = None,
    return_status:                bool                = False,
    persist:                      bool                = True,
) -> list[dict[str, Any]]:
    """
    Run the full pipeline: fetch coords → cluster → filter → score →
    optionally persist to PostGIS.

    Returns a list of placement-suggestion dicts (always).  When
    ``return_status`` is ``True``, rejected candidates (overlap / too-close)
    are included with ``status`` set so callers can inspect reasoning.
    """
    min_sep     = min_separation_km     or MINIMUM_AGENT_SEPARATION_KM
    min_cov_gap = min_coverage_distance_km or MIN_COVERAGE_DISTANCE_KM
    engine      = create_engine(_get_db_url())
    results_all: list[dict[str, Any]] = []

    # ── 1. Load existing agents ───────────────────────────────────────────────
    logger.info("Fetching existing agent coordinates …")
    df = get_agent_locations()
    df = _validate_coords(df)
    if df.empty:
        logger.warning("No agent data available for placement analysis.")
        return []

    logger.info("Loaded %d valid agent locations.", len(df))

    # ── 1a. Ward demand priors ────────────────────────────────────────────────
    demand_map = {}
    try:
        weights_df = get_ward_demand_weights()
        ward_codes_in_use = df.merge(weights_df, on="ward_code", how="left")["ward_code"]
        demand_map = dict(zip(weights_df["ward_code"], weights_df["demand_weight"]))
    except Exception as exc:
        logger.warning("Demand weights not available (%s); skipping demand weighting.", exc)

    # ── 2. KMeans clustering ───────────────────────────────────────────────
    coords = df[["latitude", "longitude"]].to_numpy(dtype=float)
    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init="auto",
    )
    kmeans.fit(coords)
    centers = kmeans.cluster_centers_

    # ── 3. Reject candidates that overlap existing agents ────────────────────
    logger.info("Filtering %d cluster centres against existing agents …", len(centers))
    ok_overlap = _candidate_overlaps_existing(engine, centers, min_sep)

    # ── 4. Enforce minimum inter-candidate spacing ─────────────────────────
    logger.info("Enforcing %.1f km minimum separation …", min_sep)
    ok_separation = _enforce_min_separation(centers, min_sep)

    # ── 5. Attach placement reasoning ────────────────────────────────────────
    for i in range(len(centers)):
        lat, lon            = float(centers[i][0]), float(centers[i][1])
        status              = "recommended"
        if not ok_overlap[i]:
            status          = "overlap_with_existing_agent"
        elif not ok_separation[i]:
            status              = "too_close_to_another_candidate"

        # demand score
        if demand_map:
            closest = int(df.apply(
                lambda r: np.linalg.norm([r.latitude - lat, r.longitude - lon]),
                axis=1,
            ).idxmin())
            demand_score = demand_map.get(closest, 0.0)
        else:
            demand_score = 0.0

        rec = dict(
            ward_code      = int(df.iloc[i].get("ward_code", 0)) if i < len(df) else 0,
            latitude       = lat,
            longitude      = lon,
            cluster_center = [lat, lon],
            demand_weight  = round(demand_score, 4),
            kmeans_inertia = round(float(kmeans.inertia_), 4),
            suggested_type = "outlet",
            status         = status,
        )
        results_all.append(rec)

    recommended    = [r for r in results_all if r["status"] == "recommended"]
    logger.info("Recommendations ready: %d of %d candidates passed all filters.",
                len(recommended), len(centers))

    # ── 6. Persist to PostGIS ────────────────────────────────────────────────
    if persist:
        _persist_to_postgis([r for r in results_all if r["status"] == "recommended"], engine)

    return results_all if return_status else recommended


def _persist_to_postgis(suggestions: list[dict[str, Any]], engine: Any) -> None:
    """Insert recommended placements into ``agent_placement_suggestions``."""
    if not suggestions:
        logger.info("No recommendations to persist.")
        return

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS agent_placement_suggestions (
                id                SERIAL PRIMARY KEY,
                ward_code         INTEGER,
                county            TEXT,
                latitude          DOUBLE PRECISION NOT NULL,
                longitude         DOUBLE PRECISION NOT NULL,
                demand_weight     DOUBLE PRECISION,
                score             DOUBLE PRECISION,
                suggested_type    TEXT,
                recommended_at    TIMESTAMPTZ      DEFAULT NOW()
            );
        """))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_suggestions_geom "
            "ON agent_placement_suggestions "
            "USING GIST (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326));"
        ))
        rows = [
            {
                "ward_code":      r.get("ward_code"),
                "latitude":       r["latitude"],
                "longitude":      r["longitude"],
                "demand_weight":  r.get("demand_weight", 0.0),
                "suggested_type": r.get("suggested_type", "outlet"),
            }
            for r in suggestions
        ]
        conn.execute(text("""
            INSERT INTO agent_placement_suggestions
                (ward_code, latitude, longitude, demand_weight, suggested_type)
            VALUES (:ward_code, :latitude, :longitude, :demand_weight, :suggested_type)
        """), rows)
    logger.info("Persisted %d recommended placements to PostGIS.", len(suggestions))


def save_suggestions(
    suggestions:   list[dict[str, Any]],
    out_dir:       Optional[str | Path] = None,
) -> dict[str, Path]:
    """Write suggestions to JSON and CSV for human review."""
    out = Path(out_dir) if out_dir else OUTPUT_DIR
    out.mkdir(parents=True, exist_ok=True)

    json_path = out / "placement_recommendations.json"
    csv_path  = out / "placement_recommendations.csv"

    with open(json_path, "w") as fh:
        json.dump(suggestions, fh, indent=2)
    pd.DataFrame(suggestions).to_csv(csv_path, index=False)

    logger.info("Saved %d recommendations → %s, %s", len(suggestions), json_path, csv_path)
    return {"json": json_path, "csv": csv_path}


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Suggest optimal new M-Pesa agent locations")
    parser.add_argument("--n-clusters",   type=int,   default=DEFAULT_N_CLUSTERS,
                        help="Number of KMeans cluster centres to generate.")
    parser.add_argument("--min-separation-km", type=float, default=MINIMUM_AGENT_SEPARATION_KM,
                        help="Minimum spacing (km) between candidate and any existing agent.")
    parser.add_argument("--include-rejected", action="store_true",
                        help="Include overlap / too-close rejections in output.")
    parser.add_argument("--no-persist",    action="store_true",
                        help="Skip writing recommendations to PostGIS.")
    parser.add_argument("--out-dir",  type=str, default=str(OUTPUT_DIR),
                        help="Directory for JSON / CSV outputs.")
    args = parser.parse_args()

    recs = suggest_new_locations(
        n_clusters          = args.n_clusters,
        min_separation_km   = args.min_separation_km,
        return_status       = args.include_rejected,
        persist             = not args.no_persist,
    )
    if recs:
        save_suggestions(recs, out_dir=args.out_dir)
    else:
        logger.warning("No recommendations generated.")
