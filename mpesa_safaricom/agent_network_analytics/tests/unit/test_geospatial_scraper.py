"""
tests/unit/test_geospatial_scraper.py

Unit tests for ingestion/geospatial_scraper.py.
All network calls are patched; no live Safaricom or Google Maps API required.
"""

import pytest
from unittest.mock import MagicMock, patch
from ingestion.geospatial_scraper import (
    GeospatialScraper,
    AgentLocation,
    AgentType,
    NetworkAnalyzer,
)


# ── helpers ──────────────────────────────────────────────────────────────────

def _agents(n: int = 5) -> list[AgentLocation]:
    grid_lat  = [-1.29 + i * 0.01 for i in range(n)]
    grid_lon  = [36.82 + i * 0.01 for i in range(n)]
    return [
        AgentLocation(
            agent_id=f"AG{i:03d}", agent_name=f"Kiosk {i}",
            latitude=grid_lat[i], longitude=grid_lon[i],
            county="Nairobi", constituency="Westlands", ward="Parklands",
            agent_type=AgentType.OUTLET, float_balance=60_000.0 + i * 10_000,
            last_transaction_date="2026-05-01",
        )
        for i in range(n)
    ]


# ── AgentLocation ─────────────────────────────────────────────────────────────

class TestAgentLocation:

    def test_enum_assignment(self):
        a = AgentLocation("1", "T", 0.0, 0.0, "", "", "", AgentType.MAIN, 0.0, "")
        assert a.agent_type == AgentType.MAIN

    def test_as_dict_contains_expected_keys(self):
        a = _agents(1)[0]
        d = a.as_dict()
        assert "agent_id" in d and "float_balance" in d


# ── GeospatialScraper ─────────────────────────────────────────────────────────

class TestGeospatialScraper:

    def setup_method(self):
        self.scraper = GeospatialScraper()

    # ── init ────────────────────────────────────────────────────────────────

    def test_default_init(self):
        assert self.scraper.api_key is None
        assert self.scraper.google_api_key is None

    def test_init_accepts_api_key(self):
        s = GeospatialScraper(api_key="test123")
        assert s.api_key == "test123"

    # ── fetch_agents_by_county raises without key ───────────────────────────

    def test_fetch_raises_without_api_key(self):
        with pytest.raises(RuntimeError, match="SAFARICOM_API_KEY"):
            GeospatialScraper().fetch_agents_by_county("047")

    def test_fetch_with_api_key_calls_requests(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "agents": [
                {"agent_id": "XYZ", "agent_name": "Demo",
                 "latitude": -1.29, "longitude": 36.82,
                 "county": "Nairobi", "constituency": "CBD", "ward": "CBD",
                 "agent_type": "outlet", "float_balance": 100_000,
                 "last_transaction_date": "2026-05-01"},
            ]
        }
        with patch("ingestion.geospatial_scraper.requests.get", return_value=mock_resp) as mock_get:
            scraper = GeospatialScraper(api_key="tok")
            result  = scraper.fetch_agents_by_county("047")
            mock_get.assert_called_once()
            assert len(result) == 1
            assert result[0].agent_id == "XYZ"

    def test_fetch_handles_http_error(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.raise_for_status.side_effect = Exception("403")
        with patch("ingestion.geospatial_scraper.requests.get", return_value=mock_resp):
            scraper = GeospatialScraper(api_key="tok")
            result  = scraper.fetch_agents_by_county("047")
        assert result == []

    # ── calculate_network_density ───────────────────────────────────────────

    def test_network_density(self):
        agents = _agents(n=10)
        density = self.scraper.calculate_network_density(agents, area_km2=5.0)
        assert density == pytest.approx(2.0)

    def test_network_density_zero_area(self):
        agents = _agents(3)
        density = self.scraper.calculate_network_density(agents, area_km2=0.0)
        assert density == 0.0

    # ── find_coverage_gaps ──────────────────────────────────────────────────

    def test_find_coverage_gaps_returns_list(self):
        agents = _agents(20)
        gaps = self.scraper.find_coverage_gaps(agents)
        assert isinstance(gaps, list)

    def test_find_coverage_gaps_fewer_than_3(self):
        gaps = self.scraper.find_coverage_gaps(_agents(2))
        assert gaps == []

    def test_coverage_gap_entries_are_tuples(self):
        gaps = self.scraper.find_coverage_gaps(_agents(10))
        assert all(isinstance(g, tuple) and len(g) == 2 for g in gaps)

    def test_coverage_gap_lat_in_range(self):
        gaps = self.scraper.find_coverage_gaps(_agents(20))
        for lat, _ in gaps:
            assert -90 <= lat <= 90


# ── calculate_float_coverage_ratio ──────────────────────────────────────────

class TestFloatCoverage:

    def test_without_db_uses_baseline(self):
        agents = _agents(3)
        scraper = GeospatialScraper()
        ratio = scraper.calculate_float_coverage_ratio(agents)
        assert ratio > 0.0
        assert ratio <= 1.0

    def test_empty_agents(self):
        scraper = GeospatialScraper()
        ratio = scraper.calculate_float_coverage_ratio([])
        assert ratio == 0.0

    # ── with live-ish DB mocked ─────────────────────────────────────────────

    def test_with_db_roundtrip(self):
        engine = MagicMock()
        with engine.connect() as conn:
            conn.__enter__.return_value = conn
            conn.__exit__.return_value    = None
            conn.execute.return_value.scalar.return_value = 7_200_000_000.0

        with patch("ingestion.geospatial_scraper.create_engine", return_value=engine):
            scraper = GeospatialScraper(db_url="sqlite:///:memory:")
            ratio = scraper.calculate_float_coverage_ratio(_agents(2))
            assert ratio > 0.0


# ── NetworkAnalyzer ──────────────────────────────────────────────────────────

class TestNetworkAnalyzer:

    def test_analyze_by_geography_total(self):
        na = NetworkAnalyzer(_agents(5))
        result = na.analyze_by_geography()
        assert result["total_agents"] == 5
        assert "by_county" in result

    def test_analyze_by_geography_groups(self):
        mix = [
            AgentLocation("1", "T", 0, 0, "Nairobi", "W", "P", AgentType.OUTLET, 0, ""),
            AgentLocation("2", "T", 0, 0, "Nairobi", "W", "P", AgentType.MAIN,   0, ""),
            AgentLocation("3", "T", 0, 0, "Mombasa", "T", "M", AgentType.KIOSK,  0, ""),
        ]
        result = NetworkAnalyzer(mix).analyze_by_geography()
        assert result["by_county"]["Nairobi"] == 2
        assert result["by_county"]["Mombasa"] == 1

    def test_analyze_float_distribution(self):
        na = NetworkAnalyzer(_agents(5))
        fd = na.analyze_float_distribution()
        assert "total_float_balance"     in fd
        assert "average_per_agent"       in fd
        assert "median_float"            in fd
        assert "agents_below_threshold"  in fd
        assert fd["agents_below_threshold"] >= 0  # all our test floats are above 50k

    def test_low_float_count(self):
        low = [AgentLocation("L", "T", 0, 0, "X", "Y", "Z", AgentType.OUTLET,
                             10_000.0, "")]
        na  = NetworkAnalyzer(low)
        fd  = na.analyze_float_distribution()
        assert fd["agents_below_threshold"] == 1

    def test_empty_agents(self):
        na = NetworkAnalyzer([])
        assert na.analyze_by_geography()["total_agents"] == 0
        fd = na.analyze_float_distribution()
        assert fd["total_float_balance"] == 0.0
