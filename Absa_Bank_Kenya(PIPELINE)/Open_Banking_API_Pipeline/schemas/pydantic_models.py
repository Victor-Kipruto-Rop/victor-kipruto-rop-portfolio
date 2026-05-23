from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Transaction(BaseModel):
    transaction_id: str = Field(..., alias="transactionId")
    amount: float
    currency: str
    description: str
    transaction_date: datetime = Field(..., alias="transactionDate")
    category: Optional[str] = None
    status: str

class Account(BaseModel):
    account_id: str = Field(..., alias="accountId")
    account_number: str = Field(..., alias="accountNumber")
    account_type: str = Field(..., alias="accountType")
    balance: float
    currency: str

class OpenBankingResponse(BaseModel):
    data: List[Transaction]
    status: str
    message: Optional[str] = None
