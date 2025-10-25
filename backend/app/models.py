from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class OptimizationType(str, Enum):
    BULK_DISCOUNT = "BULK_DISCOUNT"
    TIMING = "TIMING"
    SUBSTITUTE = "SUBSTITUTE"
    GROUP_PURCHASE = "GROUP_PURCHASE"
    SEASONAL_OPTIMIZATION = "SEASONAL_OPTIMIZATION"
    SUPPLY_RISK = "SUPPLY_RISK"
    ANOMALY_ALERT = "ANOMALY_ALERT"

class ProductInput(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    specifications: Optional[str] = Field(None, max_length=500)
    preferred_brands: Optional[List[str]] = None
    max_price: Optional[float] = Field(None, gt=0)

class FarmLocation(BaseModel):
    street_address: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=50)
    county: str = Field(..., min_length=1, max_length=100)
    zip_code: str = Field(..., min_length=5, max_length=10)
    country: str = Field(..., min_length=2, max_length=50)

class FarmInfo(BaseModel):
    location: FarmLocation
    farm_size: Optional[float] = Field(None, gt=0)
    crop_types: Optional[List[str]] = None

class EffectiveCost(BaseModel):
    p10: Optional[float] = None
    p25: Optional[float] = None
    p35: Optional[float] = None
    p50: Optional[float] = None
    p90: Optional[float] = None

class SupplierRecommendation(BaseModel):
    name: str
    price: float = Field(..., gt=0)
    delivery_terms: Optional[str] = None
    lead_time: Optional[int] = Field(None, ge=0)
    reliability: Optional[float] = Field(None, ge=0, le=1)
    moq: Optional[int] = Field(None, ge=1)
    contact_info: Optional[str] = None
    location: Optional[str] = None

class OptimizationRecommendation(BaseModel):
    type: OptimizationType
    description: str
    potential_savings: float = Field(..., ge=0)
    action_required: str
    confidence: Optional[float] = Field(None, ge=0, le=1)

class PriceAnalysis(BaseModel):
    product_id: str
    product_name: str
    effective_delivered_cost: EffectiveCost
    target_price: Optional[float] = Field(None, gt=0)
    confidence_score: float = Field(..., ge=0, le=1)
    suppliers: List[SupplierRecommendation] = []
    recommendations: List[OptimizationRecommendation] = []
    data_limitations: List[str] = []

class IndividualBudget(BaseModel):
    low: float = Field(..., ge=0)
    target: float = Field(..., ge=0)
    high: float = Field(..., ge=0)
    total_cost: float = Field(..., ge=0)

class DataAvailability(BaseModel):
    price_data_found: bool
    supplier_data_found: bool
    forecast_data_available: bool
    sentiment_data_available: bool
    missing_data_sections: List[str] = []

class ProductAnalysisResult(BaseModel):
    product_id: str
    product_name: str
    analysis: PriceAnalysis
    individual_budget: IndividualBudget
    data_availability: DataAvailability

class OverallBudget(BaseModel):
    low: float = Field(..., ge=0)
    target: float = Field(..., ge=0)
    high: float = Field(..., ge=0)
    total_cost: float = Field(..., ge=0)

class DataQualityReport(BaseModel):
    overall_data_coverage: float = Field(..., ge=0, le=1)
    reliable_products: List[str] = []
    limited_data_products: List[str] = []
    no_data_products: List[str] = []

# API Request/Response Models
class AnalyzeRequest(BaseModel):
    farm_location: FarmLocation
    products: List[ProductInput] = Field(..., min_items=1, max_items=50)

class AnalyzeResponse(BaseModel):
    product_analyses: List[ProductAnalysisResult]
    overall_budget: OverallBudget
    data_quality_report: DataQualityReport
    generated_at: datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    retryable: bool

class ErrorResponse(BaseModel):
    error: ErrorDetail
    request_id: Optional[str] = None
    timestamp: datetime

# Price Calculator Models
class PriceQuote(BaseModel):
    """Price quote from market data sources"""
    supplier: str
    product_name: str
    base_price: float = Field(..., gt=0)
    unit: str
    moq: Optional[int] = Field(None, ge=1)
    location: Optional[str] = None
    delivery_terms: Optional[str] = None
    lead_time: Optional[int] = Field(None, ge=0)
    reliability_score: Optional[float] = Field(None, ge=0, le=1)
    contact_info: Optional[str] = None
    purity_grade: Optional[str] = None
    pack_size: Optional[str] = None
    promotions: Optional[str] = None
    price_breaks: Optional[Dict[int, float]] = None
    cached_at: Optional[datetime] = None

class LogisticsCostBreakdown(BaseModel):
    """Detailed logistics cost breakdown"""
    freight_estimate: float = Field(..., ge=0)
    fuel_surcharge: float = Field(..., ge=0)
    handling_fees: float = Field(..., ge=0)
    delivery_premium: float = Field(..., ge=0)
    total: float = Field(..., ge=0)

class TaxesAndFeesBreakdown(BaseModel):
    """Detailed taxes and fees breakdown"""
    sales_tax: float = Field(..., ge=0)
    regulatory_fees: float = Field(..., ge=0)
    certification_costs: float = Field(..., ge=0)
    payment_processing: float = Field(..., ge=0)
    total: float = Field(..., ge=0)

class EffectiveCostBreakdown(BaseModel):
    """Complete effective cost calculation breakdown"""
    base_price: float = Field(..., ge=0)
    logistics_cost: float = Field(..., ge=0)
    taxes_and_fees: float = Field(..., ge=0)
    wastage_adjustment: float = Field(..., ge=0)
    total_effective_cost: float = Field(..., ge=0)
    cost_breakdown: Dict[str, float]

class ProductSpecAnalysis(BaseModel):
    """Product specification analysis results"""
    canonical_spec: str
    purity_grade: Optional[str] = None
    pack_size: Optional[str] = None
    substitute_skus: List[str] = []
    quality_adjustment: float = Field(..., ge=0)

class SupplierOfferEvaluation(BaseModel):
    """Supplier offer evaluation results"""
    supplier: str
    base_price: float = Field(..., gt=0)
    effective_price: float = Field(..., gt=0)
    moq_met: bool
    price_break_applied: bool
    promotion_applied: bool
    lead_time: int = Field(..., ge=0)
    reliability_score: float = Field(..., ge=0, le=1)
    value_score: float = Field(..., ge=0, le=1)
    moq_shortfall: Optional[int] = None
    price_break_savings: Optional[float] = None

class LocationFactors(BaseModel):
    """Location-based cost factors"""
    regional_market_density: float = Field(..., ge=0.5, le=1.5)
    distance_to_suppliers: float = Field(..., ge=0)
    local_competition_level: float = Field(..., ge=0.5, le=1.5)
    transportation_infrastructure: float = Field(..., ge=0.5, le=1.5)

class SeasonalityFactors(BaseModel):
    """Seasonality analysis for pricing"""
    current_season_multiplier: float = Field(..., ge=0.5, le=2.0)
    optimal_purchase_month: int = Field(..., ge=1, le=12)
    seasonal_savings_potential: float = Field(..., ge=0, le=100)
    planting_calendar_alignment: float = Field(..., ge=0.5, le=1.5)