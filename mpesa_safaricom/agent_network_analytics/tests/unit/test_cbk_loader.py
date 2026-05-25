"""
tests/unit/test_cbk_loader.py

Unit tests for ingestion/cbk_loader.py covering column normalisation and type
coercion — no live PostGIS connection required.
"""

import io
import textwrap

import numpy as np
import pandas as pd
import pytest

from ingestion.cbk_loader import normalise_columns, REQUIRED_COLUMNS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def raw_df() -> pd.DataFrame:
    """A typical CBK export with varied column naming."""
    data = textwrap.dedent("""\
        ID,Agent Name,County,Ward,Location,Lat,Long,Transactions,Float_Balance
        AG001,Kiosk A,Nairobi,Kangemi,Kangemi,-0.9867,35.6578,120,45000.00
        AG002,Shop B,Mombasa,Tudor,Tudor,-4.0600,39.6650,300,120000.00
        AG003,Point C,Kisumu,Kibos,Kibos,INVALID,95.0000,50,0.0
    """)
    return pd.read_csv(io.StringIO(data))


@pytest.fixture()
def tx_level_df() -> pd.DataFrame:
    """Transaction-level rows (one row per transaction, not per agent)."""
    data = textwrap.dedent("""\
        transaction_id,agent_id,transaction_type,transaction_amount,latitude,longitude
        TX001,AG001,Deposit,1000.00,-0.9867,35.6578
        TX002,AG001,Withdrawal,500.00,-0.9867,35.6578
        TX003,AG002,Deposit,2000.00,-4.0600,39.6650
    """)
    return pd.read_csv(io.StringIO(data))


# ---------------------------------------------------------------------------
# Column normalisation
# ---------------------------------------------------------------------------


class TestNormaliseColumns:
    def test_basic_rename(self, raw_df: pd.DataFrame):
        df = normalise_columns(raw_df)
        assert "agent_id"   in df.columns
        assert "agent_name" in df.columns
        assert "latitude"   in df.columns
        assert "longitude"  in df.columns
        assert "float_balance" in df.columns

    def test_missing_required_added(self, raw_df: pd.DataFrame):
        df = normalise_columns(raw_df.drop(columns=["County"]))
        for col in REQUIRED_COLUMNS:
            assert col in df.columns

    def test_latitude_coerce(self, raw_df: pd.DataFrame):
        df = normalise_columns(raw_df)
        lat_row3 = df.loc[2, "latitude"]
        assert pd.isna(lat_row3)           # "INVALID" → NaN

    def test_longitude_coerce(self, raw_df: pd.DataFrame):
        df = normalise_columns(raw_df)
        lon_row3 = df.loc[2, "longitude"]
        assert lon_row3 == pytest.approx(95.0)

    def test_transactions_coerce_to_int(self, raw_df: pd.DataFrame):
        df = normalise_columns(raw_df)
        assert df["transactions"].dtype in (np.int64, np.int32)
        assert df.loc[0, "transactions"] == 120

    def test_float_balance_coerce(self, raw_df: pd.DataFrame):
        df = normalise_columns(raw_df)
        assert df.loc[0, "float_balance"] == pytest.approx(45_000.0)

    def test_geom_wkt_valid(self, raw_df: pd.DataFrame):
        df = normalise_columns(raw_df)
        wkt = df.loc[0, "geom_wkt"]
        assert str(wkt).startswith("POINT(")
        assert "35.6578" in str(wkt) and "-0.9867" in str(wkt)

    def test_geom_wkt_null_when_missing_coords(self, raw_df: pd.DataFrame):
        df = normalise_columns(raw_df)
        # Row 2 has INVALID latitude → geom_wkt is None / NaN
        assert pd.isna(df.loc[2, "geom_wkt"])

    def test_transaction_level_columns_not_wiped(self, tx_level_df: pd.DataFrame):
        df = normalise_columns(tx_level_df)
        assert "transaction_id" in df.columns
        assert "transaction_amount" in df.columns

    def test_columns_lowercased(self):
        src = pd.DataFrame({"Agent_ID": [1], "COUNTY": ["Nairobi"]})
        df  = normalise_columns(src)
        assert "agent_id" in df.columns
        assert "county"   in df.columns

    def test_returns_dataframe(self, raw_df: pd.DataFrame):
        df = normalise_columns(raw_df)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(raw_df)   # no rows dropped by normalise step alone
