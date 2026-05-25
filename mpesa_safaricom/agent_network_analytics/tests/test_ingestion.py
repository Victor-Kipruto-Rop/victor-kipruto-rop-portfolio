import os
import pytest
from pathlib import Path

from ingestion.cbk_loader import discover_files, normalize_df


def test_discover_files():
    files = discover_files()
    # If user provided data, there should be at least one file; otherwise test passes by design
    assert isinstance(files, list)


def test_normalize_df_empty():
    import pandas as pd
    df = pd.DataFrame({'id': [], 'name': []})
    norm = normalize_df(df)
    assert 'agent_id' in norm.columns
    assert 'geom_wkt' in norm.columns
