import pytest
from schemas.pydantic_models import Transaction, OpenBankingResponse
from datetime import datetime

def test_transaction_schema():
    raw_data = {
        "transactionId": "TXN123",
        "amount": 500.0,
        "currency": "KES",
        "description": "Payment",
        "transactionDate": "2023-01-01T10:00:00",
        "status": "Completed"
    }
    txn = Transaction(**raw_data)
    assert txn.transaction_id == "TXN123"
    assert txn.amount == 500.0
    assert isinstance(txn.transaction_date, datetime)

def test_open_banking_response_schema():
    raw_response = {
        "status": "success",
        "data": [
            {
                "transactionId": "TXN123",
                "amount": 500.0,
                "currency": "KES",
                "description": "Payment",
                "transactionDate": "2023-01-01T10:00:00",
                "status": "Completed"
            }
        ]
    }
    response = OpenBankingResponse(**raw_response)
    assert response.status == "success"
    assert len(response.data) == 1
    assert response.data[0].transaction_id == "TXN123"
