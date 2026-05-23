"""Tests for ingestion modules."""
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from ingestion.cbk_stats import CBKMPesaClient


class TestCBKMPesaClient:
    """Test CBK M-Pesa client."""

    @pytest.fixture
    def client(self):
        """Create CBK client."""
        return CBKMPesaClient()

    def test_get_mpesa_statistics(self, client):
        """Test fetching M-Pesa statistics."""
        data = client.get_mpesa_statistics()
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert "date" in data.columns
        assert "total_transactions" in data.columns
        assert "total_value" in data.columns

    def test_get_agent_float_data(self, client):
        """Test fetching agent float data."""
        data = client.get_agent_float_data(region="Central")
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert "agent_id" in data.columns
        assert "float_balance" in data.columns

    def test_get_regional_summary(self, client):
        """Test fetching regional summary."""
        data = client.get_regional_summary()
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert "region" in data.columns
        assert "total_agents" in data.columns


class TestKenyaHolidaysClient:
    """Test Kenya holidays client."""

    @pytest.fixture
    def client(self):
        """Create holidays client."""
        from ingestion.calendar_client import KenyaHolidaysClient
        return KenyaHolidaysClient()

    def test_get_holidays(self, client):
        """Test fetching holidays."""
        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = [
                {"date": "2023-01-01", "name": "New Year"},
            ]
            
            holidays = client.get_holidays(2023)
            
            assert isinstance(holidays, list)

    def test_is_holiday(self, client):
        """Test holiday check."""
        from datetime import datetime
        
        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = [
                {"date": "2023-01-01", "name": "New Year"},
            ]
            
            result = client.is_holiday(datetime(2023, 1, 1))
            
            assert isinstance(result, bool)

    def test_get_business_days(self, client):
        """Test business day calculation."""
        from datetime import datetime
        
        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = []
            
            days = client.get_business_days(
                datetime(2023, 1, 1),
                datetime(2023, 1, 31),
            )
            
            assert isinstance(days, int)
            assert days > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
