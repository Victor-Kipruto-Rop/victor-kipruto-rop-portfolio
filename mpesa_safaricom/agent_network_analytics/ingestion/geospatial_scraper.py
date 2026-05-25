"""
Agent Location and Network Density Analysis for M-Pesa

Extracts geospatial data on M-Pesa agent locations, calculates
network density metrics, and analyzes coverage gaps.

Data sources
------------
- ``SAFARICOM_API_URL`` / ``SAFARICOM_API_KEY`` environment variables
  are read at instantiation time.  When not set a clear error is raised
  so the caller can distinguish "API not configured" from a network
  failure.
- Google Maps Places API is optional; pass ``google_api_key`` to the
  constructor to enable.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import requests
import numpy as np
from scipy.spatial import KDTree
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Agent classification."""
    MAIN   = "main"
    SUB    = "sub"
    OUTLET = "outlet"
    KIOSK  = "kiosk"


@dataclass
class AgentLocation:
    """Agent location record."""
    agent_id:             str
    agent_name:           str
    latitude:             float
    longitude:            float
    county:               str
    constituency:         str
    ward:                 str
    agent_type:           AgentType
    float_balance:        float
    last_transaction_date: str

    # ── private helpers used by the scraper ─────────────────────────────────
    def as_dict(self) -> dict:
        return {k: (v.value if isinstance(v, AgentType) else v)
                for k, v in asdict(self).items()}


class GeospatialScraper:
    """
    Extract geospatial data on M-Pesa agents.

    Reads ``SAFARICOM_API_URL`` and ``SAFARICOM_API_KEY`` from the
    environment if ``api_key`` is not passed explicitly.
    """

    SAFARICOM_BASE_URL: str = "https://api.safaricom.co.ke"
    SAFARICOM_ENDPOINT: str = "/agent-locator/v1/agents"
    DEFAULT_TIMEOUT: int = 15
    MIN_COVERAGE_DISTANCE_KM: float = 2.0
    MIN_DISTANCE_KM: float = 3.0          # minimum spacing between suggested agents

    def __init__(
        self,
        api_key:       Optional[str] = None,
        google_api_key: Optional[str] = None,
        db_url:        Optional[str] = None,
    ):
        self.api_key       = api_key       or os.getenv("SAFARICOM_API_KEY")
        self.google_api_key = google_api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        self.db_url        = db_url        or os.getenv("MPESA_DATABASE_URL")
        self.google_base   = "https://maps.googleapis.com/maps/api/place"
        self.agents: List[AgentLocation] = []

        if self.google_api_key:
            logger.info("Google Maps Places API enabled")
        else:
            logger.info("Google Maps Places API not configured — verification disabled")

    # ── Safaricom API ────────────────────────────────────────────────────────

    def _build_headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json", "User-Agent": "mpesa-agent-analytics/1.0"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def fetch_agents_by_county(
        self,
        county_code: str,
        max_agents:  Optional[int] = None,
    ) -> List[AgentLocation]:
        """
        Fetch all agents in *county_code* via the Safaricom agent-locator API.

        Parameters
        ----------
        county_code : ISO-3166-2 style county code (e.g. ``"047"`` for Nairobi).
        max_agents   : optional cap to avoid unbounded result-sets during development.

        Returns
        -------
        list[AgentLocation]
        """
        if not self.api_key:
            raise RuntimeError(
                "SAFARICOM_API_KEY is not set.  Export it in your environment or pass "
                "api_key=... to GeospatialScraper()."
            )

        url  = self.SAFARICOM_BASE_URL.rstrip("/") + self.SAFARICOM_ENDPOINT
        params = {"county": county_code, "per_page": 500}
        agents: List[AgentLocation] = []
        page   = 1

        logger.info("Fetching agents for county %s …", county_code)

        while True:
            params["page"] = page
            try:
                resp = requests.get(
                    url, headers=self._build_headers(), params=params,
                    timeout=self.DEFAULT_TIMEOUT,
                )
                resp.raise_for_status()
            except requests.HTTPError as exc:
                logger.error("HTTP %s for county %s page %d: %s", exc.response.status_code,
                             county_code, page, exc)
                break
            except requests.RequestException as exc:
                logger.error("Network error fetching county %s page %d: %s", county_code, page, exc)
                break

            data: Dict[str, Any] = resp.json()
            batch = data.get("agents") or data.get("data") or data.get("results") or []
            if not batch:
                logger.info("No more agents for county %s (page %d).", county_code, page)
                break

            for item in batch:
                try:
                    agents.append(AgentLocation(
                        agent_id              = str(item.get("agent_id") or item.get("id") or ""),
                        agent_name            = str(item.get("agent_name") or item.get("name") or ""),
                        latitude              = float(item.get("latitude")  or item.get("lat") or 0),
                        longitude             = float(item.get("longitude") or item.get("lon") or item.get("lng") or 0),
                        county                = str(item.get("county")     or county_code or ""),
                        constituency          = str(item.get("constituency") or ""),
                        ward                  = str(item.get("ward")        or ""),
                        agent_type            = AgentType(str(item.get("agent_type") or AgentType.OUTLET).lower()),
                        float_balance         = float(item.get("float_balance") or 0),
                        last_transaction_date = str(item.get("last_transaction_date") or ""),
                    ))
                except (TypeError, ValueError) as exc:
                    logger.warning("Skipping malformed agent record: %s — %s", item, exc)

            if max_agents and len(agents) >= max_agents:
                agents = agents[:max_agents]
                break

            page += 1
            if page % 10 == 0:
                time_sleep: float = 2.0
                logger.debug("Pausing %.0fs after %d pages to respect rate limits.", time_sleep, page)
                time.sleep(time_sleep)

        self.agents.extend(agents)
        logger.info("Fetched %d agents for county %s.", len(agents), county_code)
        return agents

    # ── Network density ───────────────────────────────────────────────────────

    def calculate_network_density(
        self,
        agents:   List[AgentLocation],
        area_km2: float,
    ) -> float:
        """Agent network density: agents per km²."""
        return len(agents) / area_km2 if area_km2 > 0 else 0.0

    # ── Coverage gaps via KD-tree ─────────────────────────────────────────────

    def find_coverage_gaps(
        self,
        agents:              List[AgentLocation],
        minimum_distance_km: float = MIN_COVERAGE_DISTANCE_KM,
    ) -> List[Tuple[float, float]]:
        """
        Identify geographic areas with sparse agent coverage using a KD-tree.

        For every pair of agents closer than ``minimum_distance_km``, the
        midpoint is flagged as a coverage gap — under-served areas tend to
        cluster along the far side of sparse agent pairs.

        Parameters
        ----------
        agents              : list of agent records.
        minimum_distance_km : cells farther from every agent than this are candidates.

        Returns
        -------
        list[(lat, lon)]
        """
        points = np.array(
            [(a.latitude, a.longitude) for a in agents if a.latitude and a.longitude]
        )
        if len(points) < 3:
            logger.info("Not enough agents for gap detection (%d).", len(points))
            return []

        # Convert km threshold to approximate degrees at Kenya's latitude
        km_per_deg_lat  = 110.574
        km_per_deg_lon  = 111.320 * np.cos(np.radians(np.mean(points[:, 0])))
        thresh_lat = minimum_distance_km / km_per_deg_lat
        thresh_lon = minimum_distance_km / km_per_deg_lon

        gaps: List[Tuple[float, float]] = []
        for i in range(len(points)):
            dists = np.sqrt(
                ((points - points[i]) / [thresh_lat, thresh_lon]) ** 2
            ).sum(axis=1)
            # agents that are too far from _this_ agent
            far = np.where(dists > 1.0)[0]          # sparse-quadrant direction
            if len(far) > 0:
                candidate = points[far].mean(axis=0)
                gaps.append((float(candidate[0]), float(candidate[1])))

        logger.info("Identified %d coverage gap candidates.", len(gaps))
        return gaps

    # ── Float coverage ────────────────────────────────────────────────────────

    def calculate_float_coverage_ratio(self, agents: List[AgentLocation]) -> float:
        """
        Compute the ratio of total agent float to total transaction volume.

        When PostGIS is configured (``db_url`` set) the monthly transaction
        volume is read from the database; otherwise a Kenyan national M-Pesa
        baseline (~KSh 1 200 bn / month) is used as a last resort.
        """
        total_float = sum(a.float_balance for a in agents)

        if self.db_url:
            try:
                from sqlalchemy import create_engine, text
                engine = create_engine(self.db_url)
                with engine.connect() as conn:
                    monthly_volume: float = float(
                        conn.execute(
                            text("SELECT COALESCE(SUM(total_transaction_amount), 0) "
                                 "FROM agents WHERE date >= CURRENT_DATE - INTERVAL '30 days';")
                        ).scalar() or 1_200_000_000_000.0
                    )
            except Exception as exc:
                logger.warning("DB float lookup failed (%s); using empirical Kenya baseline.", exc)
                monthly_volume = 1_200_000_000_000.0
        else:
            monthly_volume = 1_200_000_000_000.0

        return total_float / monthly_volume if monthly_volume > 0 else 0.0


# ── Network level analysis ────────────────────────────────────────────────────

class NetworkAnalyzer:
    """Analyse an already-loaded list of agents."""

    FLOAT_ALERT_THRESHOLD: float = 50_000.0   # KES

    def __init__(self, agents: List[AgentLocation]):
        self.agents = agents

    def analyze_by_geography(self) -> Dict[str, Any]:
        """Aggregate agent counts by county and constituency."""
        by_county: Dict[str, int]       = {}
        by_const:  Dict[str, int]       = {}
        by_type:   Dict[str, int]       = {}

        for a in self.agents:
            by_county[a.county]       = by_county.get(a.county,       0) + 1
            by_const[a.constituency]  = by_const.get(a.constituency,  0) + 1
            by_type[a.agent_type.value] = by_type.get(a.agent_type.value, 0) + 1

        return {
            "total_agents":        len(self.agents),
            "by_county":           dict(sorted(by_county.items(),    key=lambda x: -x[1])),
            "by_constituency":     dict(sorted(by_const.items(),     key=lambda x: -x[1])),
            "agent_types":         dict(sorted(by_type.items(),      key=lambda x: -x[1])),
        }

    def analyze_float_distribution(self) -> Dict[str, Any]:
        """Aggregate float metrics for the entire network."""
        total_float    = sum(a.float_balance for a in self.agents)
        agent_count    = len(self.agents)
        floats         = sorted([a.float_balance for a in self.agents])
        median_float   = floats[len(floats) // 2] if floats else 0.0
        below_threshold = self._count_low_float_agents()

        return {
            "total_float_balance":   total_float,
            "average_per_agent":     total_float / agent_count   if agent_count else 0.0,
            "median_float":          median_float,
            "agents_below_threshold":below_threshold,
            "threshold_kes":         self.FLOAT_ALERT_THRESHOLD,
        }

    def _calculate_median_float(self) -> float:
        if not self.agents:
            return 0.0
        floats = sorted(a.float_balance for a in self.agents)
        return floats[len(floats) // 2]

    def _count_low_float_agents(self) -> int:
        return sum(1 for a in self.agents
                   if a.float_balance < self.FLOAT_ALERT_THRESHOLD)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = GeospatialScraper()
    print("Agent network analysis module loaded")
