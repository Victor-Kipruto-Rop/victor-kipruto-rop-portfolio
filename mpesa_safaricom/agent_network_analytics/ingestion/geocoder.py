"""
geocoder.py

Resolve human-readable location strings (county / town / ward names)
to latitude/longitude coordinates using the Nominatim (OpenStreetMap)
geocoding service.

Raises an ImportError at import time if *geopy* is not installed so
callers know immediately what is missing, rather than getting a
cryptic AttributeError later.

Usage
-----
    from ingestion.geocoder import geocode_agent_dataframe
    df = geocode_agent_dataframe(df)   # adds 'latitude' / 'longitude' cols

Or from the command line:

    python ingestion/geocoder.py data/cbk/agents.csv --output data/cbk/agents_geocoded.csv
"""
from __future__ import annotations

import logging
import time
import argparse
from pathlib import Path

import pandas as pd

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
except ImportError:  # pragma: no cover
    raise ImportError(
        "geopy is required for geocoding.  Install it with:\n"
        "  pip install geopy"
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _make_geocoder(user_agent: str = "mpesa-agent-analytics/1.0", timeout: int = 10) -> Nominatim:
    """Return a configured :class:`~geopy.geocoders.Nominatim` instance."""
    return Nominatim(user_agent=user_agent, timeout=timeout)


def _fetch_coord(
    geocoder: Nominatim,
    query: str,
    country_bias: str = "Kenya",
    max_retries: int = 3,
    backoff_base: float = 1.0,
) -> tuple[float, float] | None:
    """
    Geocode a single query string and return ``(lat, lon)`` or ``None``.

    Retries with exponential back-off on timeout / service-unavailable
    errors so transient Nominatim failures don't crash the whole batch.
    """
    if not query or not str(query).strip():
        return None

    full_query = f"{query}, {country_bias}"
    for attempt in range(1, max_retries + 1):
        try:
            location = geocoder.geocode(full_query, exactly_one=True)
            if location:
                return float(location.latitude), float(location.longitude)
            logger.debug("No result for %r", full_query)
            return None
        except (GeocoderTimedOut, GeocoderUnavailable) as exc:
            wait = backoff_base * (2 ** (attempt - 1))
            logger.warning(
                "Geo error for %r (attempt %d/%d): %s — retrying in %.1fs",
                full_query, attempt, max_retries, exc, wait,
            )
            time.sleep(wait)
    logger.error("Giving up on %r after %d attempts", full_query, max_retries)
    return None


def geocode_agent_dataframe(
    df: pd.DataFrame,
    location_col: str = "location",
    county_col: str = "county",
    user_agent: str = "mpesa-agent-analytics/1.0",
    rate_limit_delay: float = 1.0,
    country_bias: str = "Kenya",
) -> pd.DataFrame:
    """
    Geocode rows in *df* that have ``NaN`` latitude / longitude.

    Rows that already have valid coordinates are left untouched.
    The function mutates *df* in-place and also returns it.

    Parameters
    ----------
    df :  ``pd.DataFrame`` already loaded with CBK / Safaricom agent data.
    location_col : column holding a human-readable location string.
    county_col :  column holding the county name (used as fallback).
    user_agent :  identifies the caller to Nominatim (required by TOS).
    rate_limit_delay : seconds to wait between geocoding calls (Nominatim TOS: ≤1/s).
    country_bias : default country appended to every query to reduce ambiguity.
    """
    geocoder = _make_geocoder(user_agent=user_agent)
    latitude_col = "latitude"
    longitude_col = "longitude"

    df[latitude_col] = pd.to_numeric(df.get(latitude_col), errors="coerce")
    df[longitude_col] = pd.to_numeric(df.get(longitude_col), errors="coerce")

    missing = df[latitude_col].isna() | df[longitude_col].isna()
    idx = missing[missing].index
    logger.info("Geocoding %d rows (%.1f%% of dataset)",
                len(idx), len(idx) / max(len(df), 1) * 100)

    resolved = 0
    failed = 0
    for i, row_idx in enumerate(idx):
        # Build a descending-priority query list
        location = (df.at[row_idx, location_col]
                    if location_col in df.columns else "")
        county   = (df.at[row_idx, county_col]
                    if county_col in df.columns else "")
        queries  = [q for q in [location, county] if q and str(q).strip().lower() not in ("nan", "none", "")]

        coord = None
        for q in queries:
            coord = _fetch_coord(geocoder, q, country_bias=country_bias)
            if coord:
                break

        if coord:
            df.at[row_idx, latitude_col]  = coord[0]
            df.at[row_idx, longitude_col] = coord[1]
            resolved += 1
        else:
            failed += 1

        if (i + 1) % 50 == 0:
            logger.info("Geocoding progress: %d/%d (resolved %d, failed %d)",
                        i + 1, len(idx), resolved, failed)

        if i < len(idx) - 1:          # no sleep after the last call
            time.sleep(rate_limit_delay)

    logger.info("Geocoding complete. Resolved %d / %d rows (%d failed).",
                resolved, len(idx), failed)
    return df


# ── CLI ───────────────────────────────────────────────────────────────────────

def _geocode_file(input_path: str, output_path: str | None = None) -> None:
    """Read a CSV / Excel file, geocode missing coords, write result."""
    path = Path(input_path)
    if not path.exists():
        logger.error("File not found: %s", path)
        return

    if path.suffix == '.csv':
        df = pd.read_csv(path)
    elif path.suffix in ('.xlsx', '.xls'):
        df = pd.read_excel(path)
    else:
        logger.error("Unsupported file type: %s", path.suffix)
        return

    df = geocode_agent_dataframe(df)

    out = Path(output_path) if output_path else path
    if out.suffix == '.csv':
        df.to_csv(out, index=False)
    else:
        df.to_excel(out, index=False)
    logger.info("Saved geocoded data → %s", out)


if __name__ == '__main__':
    _parser = argparse.ArgumentParser(description="Geocode missing lat/lng in agent data")
    _parser.add_argument("input",  help="Path to CSV or Excel file")
    _parser.add_argument("--output", default=None, help="Output path (default: overwrite input)")
    argv = _parser.parse_args()
    _geocode_file(argv.input, argv.output)
