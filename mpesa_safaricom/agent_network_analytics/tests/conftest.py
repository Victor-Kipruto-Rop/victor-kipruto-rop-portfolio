"""
tests/conftest.py

Shared pytest fixtures for the Agent_Network_Analytics test suite.
"""
import os
import sys
import types

import pytest

# ---------------------------------------------------------------------------
# Ensure the project root and ingestion/ package are importable when pytest
# is run from the repo root (``cd``) or from inside ``tests/``.
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INGESTION_DIR = os.path.join(PROJECT_ROOT, "ingestion")
SPATIAL_DIR   = os.path.join(PROJECT_ROOT, "spatial")

for _p in (PROJECT_ROOT, INGESTION_DIR, SPATIAL_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Stub heavy optional deps so tests can import modules without installing
# the full runtime stack (Airflow is especially heavy).
for _m in ("airflow", "airflow.models", "airflow.operators",
           "airflow.operators.bash", "airflow.operators.python",
           "airflow.utils", "airflow.utils.email",
           "airflow.utils.trigger_rule", "airflow.utils.task_group",
           "sqlalchemy_geoalchemy2_geoalchemy2"):
    if _m not in sys.modules:
        _mod = types.ModuleType(_m)
        sys.modules[_m] = _mod

# Provide minimal dag attribute for DAG itertools
import airflow
airflow.DAG = type("DAG", (), {"__init__": lambda *a, **kw: None})

# Set up a throwaway DB_URL for tests that don't hit PostGIS
os.environ.setdefault("MPESA_DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture()
def sample_agent_dict() -> dict:
    """Return a representative agent record dict."""
    return {
        "agent_id": "AG-001",
        "agent_name": "Juma Opticals Westlands",
        "latitude":  -1.2543,
        "longitude":  36.8032,
        "county":     "Nairobi",
        "constituency": "Westlands",
        "ward":       "Parklands / Highridge",
        "agent_type": "outlet",
        "float_balance": 85_000.0,
        "last_transaction_date": "2026-05-19",
    }
