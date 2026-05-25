"""
tests/unit/test_geocoder.py

Unit tests for ingestion/geocoder.py — no live Nominatim network calls.
Uses unittest.mock to patch geopy.
"""

import io
import textwrap

import pandas as pd
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ingestion.geocoder import geocode_agent_dataframe


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_df(rows: list[dict]) -> pd.DataFrame:
    """Build a minimal agent DataFrame with the columns geocoder expects."""
    return pd.DataFrame(rows)


class FakeLoc:
    def __init__(self, lat, lon, address=None):
        self.latitude  = lat
        self.longitude = lon
        self.address   = address or "Kenya"


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestGeocodeAgentDataframe:

    def test_existing_coords_untouched(self):
        df = _make_df([{"agent_id": "A1", "location": "Nairobi", "latitude": -1.29, "longitude": 36.82}])
        result = geocode_agent_dataframe(df, rate_limit_delay=0.0)
        assert result.loc[0, "latitude"]  == pytest.approx(-1.29)
        assert result.loc[0, "longitude"] == pytest.approx(36.82)

    def test_missing_coords_filled(self):
        df = _make_df([{"agent_id": "A1", "location": "Nairobi", "latitude": None, "longitude": None}])
        mock_loc = FakeLoc(-1.2921, 36.8219, "Nairobi, Kenya")

        with patch("ingestion.geocoder.Nominatim") as mock_nom:
            mock_nom.return_value.geocode.return_value = mock_loc
            result = geocode_agent_dataframe(df, rate_limit_delay=0.0)

        assert result.loc[0, "latitude"]  == pytest.approx(-1.2921)
        assert result.loc[0, "longitude"] == pytest.approx(36.8219)

    def test_county_fallback_on_geocode_failure(self):
        df = _make_df([{"agent_id": "A1", "location": None, "county": "Mombasa", "latitude": None, "longitude": None}])
        mock_loc = FakeLoc(-4.0435, 39.6682, "Mombasa, Kenya")

        with patch("ingestion.geocoder.Nominatim") as mock_nom:
            mock_nom.return_value.geocode.return_value = mock_loc
            result = geocode_agent_dataframe(df, rate_limit_delay=0.0)

        assert result.loc[0, "latitude"]  == pytest.approx(-4.0435)
        assert result.loc[0, "longitude"] == pytest.approx(39.6682)

    def test_null_query_skipped(self):
        df = _make_df([{"agent_id": "A1", "location": "", "county": "", "latitude": None, "longitude": None}])

        with patch("ingestion.geocoder.Nominatim") as mock_nom:
            geocode_agent_dataframe(df, rate_limit_delay=0.0)

        mock_nom.return_value.geocode.assert_not_called()

    def test_no_new_rows_returns_df(self):
        df = pd.DataFrame({"agent_id": ["A1"], "latitude": [1.0], "longitude": [1.0]})
        result = geocode_agent_dataframe(df, rate_limit_delay=0.0)
        assert len(result) == 1

    def test_returns_same_dataframe(self):
        df = _make_df([{"agent_id": "A1", "location": "Nakuru", "latitude": None, "longitude": None}])
        mock_loc = FakeLoc(-0.3006, 36.0700, "Nakuru, Kenya")

        with patch("ingestion.geocoder.Nominatim") as mock_nom:
            mock_nom.return_value.geocode.return_value = mock_loc
            result = geocode_agent_dataframe(df, rate_limit_delay=0.0)

        assert result is df          # in-place mutation

    def test_zero_rows_empty_df(self):
        df = pd.DataFrame(columns=["agent_id", "location", "county", "latitude", "longitude"])
        result = geocode_agent_dataframe(df, rate_limit_delay=0.0)
        assert result.empty
