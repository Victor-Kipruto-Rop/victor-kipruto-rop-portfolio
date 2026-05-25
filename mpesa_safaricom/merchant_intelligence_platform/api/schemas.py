"""
FastAPI schemas for Merchant Intelligence Platform API

Defines request/response Pydantic models for merchant data endpoints.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MerchantType(str, Enum):
    """Merchant classification."""
    RETAIL = "retail"
    WHOLESALE = "wholesale"
    SERVICE = "service"
    TRANSPORT = "transport"
    HOSPITALITY = "hospitality"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    GOVERNMENT = "government"
    OTHER = "other"


class MerchantSegment(str, Enum):
    """Merchant segment classification."""
    HIGH_VALUE = "high_value"
    GROWTH = "growth"
    STABLE = "stable"
    AT_RISK = "at_risk"
    DORMANT = "dormant"


# Request models

class MerchantSearchRequest(BaseModel):
    """Search for merchants by criteria."""
    
    query: Optional[str] = Field(None, description="Merchant name or ID")
    merchant_type: Optional[MerchantType] = None
    segment: Optional[MerchantSegment] = None
    min_monthly_volume: Optional[float] = Field(None, ge=0)
    max_monthly_volume: Optional[float] = Field(None, ge=0)
    county: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class MerchantProfileUpdateRequest(BaseModel):
    """Update merchant profile information."""
    
    name: Optional[str] = None
    merchant_type: Optional[MerchantType] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    county: Optional[str] = None
    business_category: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=1000)


# Response models

class MerchantSummary(BaseModel):
    """Basic merchant information."""
    
    merchant_id: str
    name: str
    merchant_type: MerchantType
    segment: MerchantSegment
    monthly_transaction_volume: float
    monthly_transaction_count: int
    average_transaction_value: float
    
    class Config:
        from_attributes = True


class MerchantProfile(MerchantSummary):
    """Complete merchant profile."""
    
    county: str
    constituency: str
    ward: str
    business_category: str
    registration_date: datetime
    last_transaction_date: datetime
    
    # Performance metrics
    transaction_success_rate: float
    average_daily_transactions: float
    growth_rate_30d: float
    growth_rate_90d: float
    
    # Risk metrics
    fraud_flag: bool
    duplicate_merchant_flag: bool
    kyc_verification_status: str
    
    # Contact
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime


class MerchantPerformance(BaseModel):
    """Merchant performance metrics."""
    
    merchant_id: str
    merchant_name: str
    
    # Transaction metrics
    transactions_today: int
    transactions_week: int
    transactions_month: int
    
    volume_today: float
    volume_week: float
    volume_month: float
    
    # Trend metrics
    daily_avg_7d: float
    daily_avg_30d: float
    weekly_growth_percent: float
    monthly_growth_percent: float
    
    # Health metrics
    health_score: float  # 0-100
    churn_risk: bool
    recommendation: str


class MerchantSegmentAnalysis(BaseModel):
    """Segment-level analysis."""
    
    segment: MerchantSegment
    merchant_count: int
    total_volume: float
    average_volume_per_merchant: float
    average_transactions_per_merchant: int
    
    volume_contribution_percent: float
    transaction_contribution_percent: float
    
    growth_rate_month_over_month: float
    churn_rate: float
    avg_health_score: float


class MerchantSearchResponse(BaseModel):
    """Paginated search results."""
    
    results: List[MerchantSummary]
    total_count: int
    limit: int
    offset: int
    has_more: bool


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error_code: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Aggregation responses

class MerchantDashboard(BaseModel):
    """Dashboard aggregation."""
    
    total_merchants: int
    active_merchants: int
    total_volume_mtd: float
    total_transactions_mtd: int
    
    by_segment: List[MerchantSegmentAnalysis]
    by_type: dict  # merchant_type -> count
    
    top_merchants: List[MerchantSummary]
    at_risk_merchants: List[MerchantSummary]
    
    generated_at: datetime = Field(default_factory=datetime.now)


if __name__ == "__main__":
    # Test model instantiation
    merchant = MerchantProfile(
        merchant_id="M001",
        name="Test Merchant",
        merchant_type=MerchantType.RETAIL,
        segment=MerchantSegment.GROWTH,
        monthly_transaction_volume=500000,
        monthly_transaction_count=150,
        average_transaction_value=3333.33,
        county="Nairobi",
        constituency="Westlands",
        ward="Kilimani",
        business_category="Retail",
        registration_date=datetime.now(),
        last_transaction_date=datetime.now(),
        transaction_success_rate=0.98,
        average_daily_transactions=5.0,
        growth_rate_30d=0.15,
        growth_rate_90d=0.25,
        fraud_flag=False,
        duplicate_merchant_flag=False,
        kyc_verification_status="verified",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    print(merchant.model_dump_json(indent=2))
