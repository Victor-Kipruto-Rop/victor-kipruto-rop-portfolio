import pytest
from datetime import datetime
from ingestion.kafka_producer import get_transaction

def test_transaction_generation():
    """Test that the generated transaction has all required fields."""
    tx = get_transaction()
    
    assert 'transaction_id' in tx
    assert 'amount' in tx
    assert 'county' in tx
    assert 'transaction_type' in tx
    assert isinstance(tx['amount'], (int, float))
    assert tx['amount'] > 0

def test_transaction_county_validity():
    """Test that the county is within the expected set."""
    expected_counties = ['Nairobi', 'Mombasa', 'Kiambu', 'Nakuru', 'Uasin Gishu', 'Kisumu', 'Kajiado']
    tx = get_transaction()
    assert tx['county'] in expected_counties
