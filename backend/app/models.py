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


# AWS BI Data Models

class ForecastPrediction(BaseModel):
    """Individual forecast prediction point"""
    date: str = Field(..., description="ISO date string for prediction")
    predicted_price: float = Field(..., gt=0)
    confidence_interval: Dict[str, float] = Field(
        ..., 
        description="Contains 'lower' and 'upper' confidence bounds"
    )

class ForecastResult(BaseModel):
    """Amazon Forecast service results"""
    predictions: List[ForecastPrediction] = []
    trend: str = Field(..., description="Overall trend: 'declining', 'increasing', 'stable'")
    confidence: float = Field(..., ge=0, le=1, description="Overall forecast confidence")
    lowest_price_date: Optional[str] = Field(None, description="Date of predicted lowest price")
    predicted_lowest_price: Optional[float] = Field(None, gt=0)
    decline_percentage: Optional[float] = Field(None, ge=0, le=100)
    forecast_horizon_days: int = Field(..., ge=1, le=365)
    model_accuracy: Optional[float] = Field(None, ge=0, le=1)
    seasonality_detected: bool = False
    data_quality_score: float = Field(..., ge=0, le=1)

class SentimentFactor(BaseModel):
    """Individual sentiment factor analysis"""
    factor: str = Field(..., description="Factor name (e.g., 'weather', 'fuel_prices')")
    sentiment: str = Field(..., description="POSITIVE, NEGATIVE, or NEUTRAL")
    confidence: float = Field(..., ge=0, le=1)
    impact_description: str

class SentimentAnalysis(BaseModel):
    """AWS Comprehend sentiment analysis results"""
    overall_sentiment: str = Field(..., description="POSITIVE, NEGATIVE, or NEUTRAL")
    sentiment_score: float = Field(..., ge=0, le=1)
    supply_risk_score: float = Field(..., ge=0, le=1)
    demand_outlook: str = Field(..., description="Strong/Moderate/Weak demand outlook")
    risk_level: str = Field(..., description="LOW, MEDIUM, or HIGH risk level")
    key_factors: List[SentimentFactor] = []
    confidence_score: float = Field(..., ge=0, le=1)
    news_sources_analyzed: int = Field(..., ge=0)
    analysis_date: datetime

class CorrelationFactor(BaseModel):
    """External factor correlation analysis"""
    factor: str = Field(..., description="External factor name")
    correlation_strength: float = Field(..., ge=-1, le=1)
    impact_description: str

class TrendAnalysis(BaseModel):
    """Price trend analysis from QuickSight"""
    direction: str = Field(..., description="increasing, decreasing, or stable")
    strength: float = Field(..., ge=0, le=1, description="Trend strength indicator")
    duration_days: int = Field(..., ge=1)
    statistical_significance: float = Field(..., ge=0, le=1)

class QuickSightInsights(BaseModel):
    """AWS QuickSight ML insights and analytics"""
    price_anomaly_detected: bool = False
    anomaly_description: Optional[str] = None
    anomaly_confidence: Optional[float] = Field(None, ge=0, le=1)
    seasonal_pattern_detected: bool = False
    optimal_purchase_month: Optional[str] = None
    seasonal_savings_potential: Optional[float] = Field(None, ge=0, le=100)
    pattern_confidence: Optional[float] = Field(None, ge=0, le=1)
    trend_analysis: Optional[TrendAnalysis] = None
    correlations: List[CorrelationFactor] = []
    dashboard_url: Optional[str] = None
    insights_generated_at: datetime
    data_freshness_score: float = Field(..., ge=0, le=1)

class AWSBIConfidenceFactors(BaseModel):
    """Confidence score calculation factors from AWS BI services"""
    forecast_confidence: float = Field(..., ge=0, le=1)
    sentiment_confidence: float = Field(..., ge=0, le=1)
    quicksight_insights_confidence: float = Field(..., ge=0, le=1)
    data_completeness: float = Field(..., ge=0, le=1)
    source_reliability: float = Field(..., ge=0, le=1)
    temporal_relevance: float = Field(..., ge=0, le=1)

class AWSBIAnalysisResult(BaseModel):
    """Combined AWS BI analysis results for a product"""
    product_name: str
    forecast_result: Optional[ForecastResult] = None
    sentiment_analysis: Optional[SentimentAnalysis] = None
    quicksight_insights: Optional[QuickSightInsights] = None
    confidence_factors: AWSBIConfidenceFactors
    overall_bi_confidence: float = Field(..., ge=0, le=1)
    analysis_timestamp: datetime
    aws_services_used: List[str] = []
    processing_time_seconds: float = Field(..., ge=0)

# Advanced Optimization Features Models (Task 7.2)

class PriceAlertRequest(BaseModel):
    """Request model for creating price alerts"""
    product_name: str = Field(..., min_length=1, max_length=200)
    target_price: float = Field(..., gt=0)
    farm_location: FarmLocation
    contact_email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    alert_type: str = Field(default="price_drop", description="Type of alert: price_drop, price_rise, availability")
    threshold_percentage: Optional[float] = Field(None, ge=0, le=100, description="Percentage threshold for alerts")
    expiry_date: Optional[datetime] = Field(None, description="When the alert should expire")

class PriceAlert(BaseModel):
    """Price alert data model"""
    alert_id: str
    product_name: str
    target_price: float
    current_price: Optional[float] = None
    farm_location: FarmLocation
    contact_email: str
    alert_type: str
    threshold_percentage: Optional[float] = None
    status: str = Field(default="active", description="active, triggered, expired, cancelled")
    created_at: datetime
    last_checked: Optional[datetime] = None
    notifications_sent: int = Field(default=0)
    expiry_date: Optional[datetime] = None

class BundlingAnalysisRequest(BaseModel):
    """Request model for cross-product bundling analysis"""
    products: List[ProductInput] = Field(..., min_items=2, max_items=20)
    farm_location: FarmLocation
    max_suppliers: Optional[int] = Field(default=5, ge=1, le=10)
    include_group_purchasing: bool = Field(default=True)

class BundlingOpportunity(BaseModel):
    """Individual bundling opportunity"""
    supplier: str
    products_included: List[str]
    individual_total_cost: float = Field(..., ge=0)
    bundle_cost: float = Field(..., ge=0)
    savings_amount: float = Field(..., ge=0)
    savings_percentage: float = Field(..., ge=0, le=100)
    minimum_order_quantity: str
    delivery_terms: str
    bundle_validity: str
    bundle_type: str = Field(description="supplier_bundle, group_purchase, cooperative")
    confidence_score: float = Field(..., ge=0, le=1)

class BundlingAnalysisResponse(BaseModel):
    """Response model for bundling analysis"""
    analysis_id: str
    products_analyzed: int
    bundling_opportunities: List[BundlingOpportunity]
    total_opportunities: int
    max_potential_savings: float = Field(..., ge=0)
    recommended_bundle: Optional[BundlingOpportunity] = None
    analysis_date: datetime

class PurchaseTrackingRequest(BaseModel):
    """Request model for purchase tracking"""
    product_name: str = Field(..., min_length=1, max_length=200)
    actual_price: float = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    supplier: str = Field(..., min_length=1, max_length=200)
    purchase_date: str = Field(..., description="ISO date string")
    target_price: Optional[float] = Field(None, gt=0)
    analysis_session_id: Optional[str] = None
    delivery_date: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=1000)

class PurchaseRecord(BaseModel):
    """Purchase record data model"""
    purchase_id: str
    product_name: str
    supplier: str
    actual_price: float = Field(..., gt=0)
    target_price: Optional[float] = Field(None, gt=0)
    quantity: float = Field(..., gt=0)
    total_cost: float = Field(..., ge=0)
    purchase_date: str
    delivery_date: Optional[str] = None
    payment_terms: Optional[str] = None
    price_variance: float
    price_variance_percentage: float
    performance_rating: str = Field(description="excellent, good, needs_improvement, no_target_available")
    recorded_at: datetime
    notes: Optional[str] = None

class PurchasePerformanceSummary(BaseModel):
    """Purchase performance summary"""
    rating: str
    savings_vs_target: float = Field(..., ge=0)
    overspend_vs_target: float = Field(..., ge=0)
    variance_percentage: float
    total_purchases: int = Field(default=1)
    average_performance: Optional[float] = Field(None, ge=0, le=1)

class PurchaseTrackingResponse(BaseModel):
    """Response model for purchase tracking"""
    purchase_id: str
    purchase_record: PurchaseRecord
    performance_summary: PurchasePerformanceSummary
    insights: List[str]
    recommendations: List[str]
    comparison_data: Optional[Dict[str, Any]] = None

class FinancingOption(BaseModel):
    """Individual financing option"""
    option: str
    total_cost: float = Field(..., ge=0)
    upfront_payment: float = Field(..., ge=0)
    monthly_payment: float = Field(..., ge=0)
    total_interest: float = Field(..., ge=0)
    savings_vs_full_price: float = Field(..., ge=0)
    cash_flow_impact: str
    recommendation_score: int = Field(..., ge=0, le=100)
    pros: List[str]
    cons: List[str]
    terms_months: Optional[int] = Field(None, ge=0)
    interest_rate: Optional[float] = Field(None, ge=0)

class FinancingAnalysisRequest(BaseModel):
    """Request model for financing analysis"""
    total_purchase_amount: float = Field(..., gt=0)
    cash_available: float = Field(..., ge=0)
    credit_score: Optional[int] = Field(None, ge=300, le=850)
    preferred_terms_months: Optional[int] = Field(None, ge=1, le=60)
    risk_tolerance: str = Field(default="medium", description="low, medium, high")
    seasonal_cash_flow: Optional[Dict[str, float]] = Field(None, description="Monthly cash flow projections")

class FinancingRecommendation(BaseModel):
    """Financing recommendation"""
    recommended_option: str
    reasoning: str
    key_benefits: List[str]
    considerations: List[str]
    cash_flow_analysis: Optional[Dict[str, Any]] = None

class FinancingAnalysisResponse(BaseModel):
    """Response model for financing analysis"""
    analysis_id: str
    purchase_amount: float
    cash_available: float
    financing_options: List[FinancingOption]
    recommendation: FinancingRecommendation
    analysis_date: datetime
    notes: List[str]

# Data transformation models for AWS service inputs/outputs

class ForecastDatasetInput(BaseModel):
    """Input format for Amazon Forecast dataset creation"""
    timestamp: str = Field(..., description="ISO timestamp")
    target_value: float = Field(..., description="Price value")
    item_id: str = Field(..., description="Product identifier")
    location: Optional[str] = None
    category: Optional[str] = None

class ComprehendTextInput(BaseModel):
    """Input format for AWS Comprehend analysis"""
    text: str = Field(..., min_length=1, max_length=5000)
    language_code: str = Field(default="en", description="Language code for analysis")
    source_url: Optional[str] = None
    publication_date: Optional[datetime] = None
    source_type: str = Field(default="news", description="Type of source: news, report, social")

class QuickSightDataInput(BaseModel):
    """Input format for QuickSight data analysis"""
    product_name: str
    price_history: List[Dict[str, Any]] = Field(..., description="Historical price data points")
    market_factors: Dict[str, Any] = Field(default_factory=dict)
    location_data: Optional[Dict[str, Any]] = None
    seasonal_indicators: Optional[Dict[str, Any]] = None