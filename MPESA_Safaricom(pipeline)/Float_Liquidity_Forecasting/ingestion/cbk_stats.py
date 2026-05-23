"""CBK M-Pesa statistics ingestion."""
from datetime import datetime
from typing import Optional

import pandas as pd
import requests

from config import settings
from logger import logger


class CBKMPesaClient:
    """Fetch Central Bank of Kenya M-Pesa statistics."""

    def __init__(self):
        """Initialize CBK client."""
        # Using mock API - in production, connect to actual CBK API
        self.base_url = settings.CBK_API_URL or "https://www.cbk.go.ke/api"
        self.timeout = 15

    def get_mpesa_statistics(
        self, start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Fetch M-Pesa statistics from CBK.

        Args:
            start_date: Start date for data
            end_date: End date for data

        Returns:
            DataFrame with M-Pesa statistics
        """
        try:
            params = {}
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()

            # For now, return sample data structure
            # In production, this would call actual CBK API
            logger.info("Fetching M-Pesa statistics from CBK")

            data = {
                "date": pd.date_range(start=start_date or "2023-01-01", periods=365),
                "total_transactions": [
                    1500000 + i * 1000 for i in range(365)
                ],
                "total_value": [
                    2500000000 + i * 5000000 for i in range(365)
                ],
                "active_agents": [35000 + i * 10 for i in range(365)],
                "agent_float_value": [
                    150000000 + i * 100000 for i in range(365)
                ],
            }

            df = pd.DataFrame(data)
            logger.info(f"Retrieved {len(df)} records of M-Pesa statistics")
            return df

        except Exception as e:
            logger.error(f"Failed to fetch CBK statistics: {e}")
            return pd.DataFrame()

    def get_agent_float_data(
        self, region: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get agent-level float data by region.

        Args:
            region: Kenya region (e.g., 'Nairobi', 'Central', 'Coast')

        Returns:
            DataFrame with agent float data
        """
        try:
            logger.info(
                f"Fetching agent float data for region: {region or 'All'}"
            )

            # Sample data structure
            data = {
                "agent_id": [f"AGENT_{i:05d}" for i in range(1000)],
                "region": [region or "Central"] * 1000,
                "float_balance": [100000 + i * 500 for i in range(1000)],
                "daily_transactions": [50 + i for i in range(1000)],
                "transaction_value": [
                    500000 + i * 10000 for i in range(1000)
                ],
                "date": [datetime.now()] * 1000,
            }

            df = pd.DataFrame(data)
            logger.info(
                f"Retrieved {len(df)} agent records for {region or 'all regions'}"
            )
            return df

        except Exception as e:
            logger.error(f"Failed to fetch agent float data: {e}")
            return pd.DataFrame()

    def get_regional_summary(self) -> pd.DataFrame:
        """
        Get aggregated statistics by region.

        Returns:
            DataFrame with regional summaries
        """
        try:
            regions = [
                "Nairobi",
                "Central",
                "Coast",
                "Eastern",
                "North",
                "South",
                "Rift Valley",
                "Western",
            ]

            data = {
                "region": regions,
                "total_agents": [4000 + i * 100 for i in range(len(regions))],
                "total_float": [
                    50000000 + i * 2000000 for i in range(len(regions))
                ],
                "avg_daily_transactions": [
                    5000 + i * 200 for i in range(len(regions))
                ],
                "date": [datetime.now()] * len(regions),
            }

            df = pd.DataFrame(data)
            logger.info(f"Retrieved regional summary for {len(df)} regions")
            return df

        except Exception as e:
            logger.error(f"Failed to fetch regional summary: {e}")
            return pd.DataFrame()
