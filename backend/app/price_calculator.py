"""
Price Calculator Module

Implements comprehensive economic analysis for agricultural product pricing,
including effective delivered cost calculation, logistics analysis, and 
statistical price range calculations.
"""

import statistics
import math
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .models import (
    FarmLocation, 
    EffectiveCost, 
    SupplierRecommendation,
    ProductInput
)


class ProductCategory(str, Enum):
    """Product categories for different calculation approaches"""
    SEEDS = "seeds"
    FERTILIZER = "fertilizer"
    PESTICIDES = "pesticides"
    EQUIPMENT = "equipment"
    FUEL = "fuel"
    OTHER = "other"


@dataclass
class PriceQuote:
    """Raw price quote from market data"""
    supplier: str
    product_name: str
    base_price: float
    unit: str
    moq: Optional[int] = None
    location: Optional[str] = None
    delivery_terms: Optional[str] = None
    lead_time: Optional[int] = None
    reliability_score: Optional[float] = None
    contact_info: Optional[str] = None
    purity_grade: Optional[str] = None
    pack_size: Optional[str] = None
    promotions: Optional[str] = None
    price_breaks: Optional[Dict[int, float]] = None
    cached_at: Optional[datetime] = None


@dataclass
class LogisticsCost:
    """Breakdown of logistics costs"""
    freight_estimate: float
    fuel_surcharge: float
    handling_fees: float
    delivery_premium: float
    total: float


@dataclass
class TaxesAndFees:
    """Breakdown of taxes and regulatory fees"""
    sales_tax: float
    regulatory_fees: float
    certification_costs: float
    payment_processing: float
    total: float


@dataclass
class ProductSpecAnalysis:
    """Product specification analysis results"""
    canonical_spec: str
    purity_grade: Optional[str]
    pack_size: Optional[str]
    substitute_skus: List[str]
    quality_adjustment: float  # Multiplier for price adjustment


@dataclass
class LocationFactors:
    """Location-based cost factors"""
    regional_market_density: float  # 0.8-1.2 multiplier
    distance_to_suppliers: float   # km average
    local_competition_level: float # 0.9-1.1 multiplier
    transportation_infrastructure: float # 0.95-1.05 multiplier


@dataclass
class SeasonalityFactors:
    """Seasonality analysis for pricing"""
    current_season_multiplier: float  # 0.8-1.3 based on season
    optimal_purchase_month: int      # 1-12
    seasonal_savings_potential: float # percentage
    planting_calendar_alignment: float # 0.9-1.1 multiplier


class PriceCalculator:
    """
    Comprehensive price calculator implementing economic analysis framework
    from the design document requirements 4.1-4.7.
    """
    
    def __init__(self):
        # Wastage factors by product category (percentage)
        self.wastage_factors = {
            ProductCategory.SEEDS: 0.02,      # 2% wastage
            ProductCategory.FERTILIZER: 0.01,  # 1% wastage  
            ProductCategory.PESTICIDES: 0.005, # 0.5% wastage
            ProductCategory.EQUIPMENT: 0.0,    # No wastage
            ProductCategory.FUEL: 0.01,        # 1% wastage
            ProductCategory.OTHER: 0.01        # 1% default
        }
        
        # Base tax rates by state (simplified - would use real tax API)
        self.state_tax_rates = {
            "CA": 0.0725, "TX": 0.0625, "FL": 0.06, "NY": 0.08,
            "IL": 0.0625, "PA": 0.06, "OH": 0.0575, "GA": 0.04,
            "NC": 0.0475, "MI": 0.06, "NJ": 0.06625, "VA": 0.053,
            "WA": 0.065, "AZ": 0.056, "MA": 0.0625, "TN": 0.07,
            "IN": 0.07, "MO": 0.0423, "MD": 0.06, "WI": 0.05
        }
        
        # Seasonal multipliers by month for different product categories
        self.seasonal_multipliers = {
            ProductCategory.SEEDS: {
                1: 0.95, 2: 0.90, 3: 1.10, 4: 1.20, 5: 1.15,
                6: 1.05, 7: 0.95, 8: 0.90, 9: 0.95, 10: 1.00,
                11: 0.95, 12: 0.90
            },
            ProductCategory.FERTILIZER: {
                1: 1.05, 2: 1.10, 3: 1.20, 4: 1.25, 5: 1.15,
                6: 1.00, 7: 0.95, 8: 0.90, 9: 0.95, 10: 1.00,
                11: 1.05, 12: 1.00
            },
            ProductCategory.PESTICIDES: {
                1: 1.00, 2: 1.05, 3: 1.15, 4: 1.20, 5: 1.25,
                6: 1.10, 7: 1.00, 8: 0.95, 9: 0.95, 10: 1.00,
                11: 1.00, 12: 1.00
            }
        }

    def calculate_effective_delivered_cost(
        self, 
        quote: PriceQuote, 
        farm_location: FarmLocation,
        product_input: ProductInput
    ) -> Dict[str, float]:
        """
        Calculate comprehensive effective delivered cost per unit.
        
        Requirements: 4.1, 4.2, 4.3
        """
        # 1. Normalize base price to standard unit
        base_price = self._normalize_to_base_uom(quote, product_input)
        
        # 2. Calculate logistics costs
        logistics = self._calculate_logistics_cost(quote, farm_location)
        
        # 3. Calculate taxes and fees
        taxes_fees = self._calculate_taxes_and_fees(quote, farm_location, base_price)
        
        # 4. Apply wastage factor
        product_category = self._categorize_product(product_input.name)
        wastage_factor = self.wastage_factors.get(product_category, 0.01)
        wastage_adjustment = base_price * wastage_factor
        
        # 5. Calculate total effective cost
        total_cost = base_price + logistics.total + taxes_fees.total + wastage_adjustment
        
        return {
            "base_price": base_price,
            "logistics_cost": logistics.total,
            "taxes_and_fees": taxes_fees.total,
            "wastage_adjustment": wastage_adjustment,
            "total_effective_cost": total_cost,
            "cost_breakdown": {
                "freight": logistics.freight_estimate,
                "fuel_surcharge": logistics.fuel_surcharge,
                "handling": logistics.handling_fees,
                "delivery_premium": logistics.delivery_premium,
                "sales_tax": taxes_fees.sales_tax,
                "regulatory_fees": taxes_fees.regulatory_fees,
                "certification": taxes_fees.certification_costs,
                "payment_processing": taxes_fees.payment_processing
            }
        }

    def calculate_price_ranges(self, effective_costs: List[float]) -> EffectiveCost:
        """
        Calculate statistical price ranges using percentiles.
        Removes outliers using MAD (Median Absolute Deviation).
        
        Requirements: 4.1, 4.3
        """
        if not effective_costs:
            return EffectiveCost()
        
        # Remove outliers using MAD method
        cleaned_costs = self._remove_outliers_mad(effective_costs)
        
        if len(cleaned_costs) < 2:
            # Not enough data for statistical analysis
            avg_cost = sum(effective_costs) / len(effective_costs)
            return EffectiveCost(
                p10=avg_cost * 0.9,
                p25=avg_cost * 0.95,
                p35=avg_cost * 0.97,
                p50=avg_cost,
                p90=avg_cost * 1.1
            )
        
        # Calculate percentiles
        sorted_costs = sorted(cleaned_costs)
        n = len(sorted_costs)
        
        def percentile(data: List[float], p: float) -> float:
            """Calculate percentile using linear interpolation"""
            if not data:
                return 0.0
            k = (len(data) - 1) * p / 100
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return data[int(k)]
            d0 = data[int(f)] * (c - k)
            d1 = data[int(c)] * (k - f)
            return d0 + d1
        
        return EffectiveCost(
            p10=percentile(sorted_costs, 10),
            p25=percentile(sorted_costs, 25),
            p35=percentile(sorted_costs, 35),
            p50=percentile(sorted_costs, 50),
            p90=percentile(sorted_costs, 90)
        )

    def calculate_confidence_score(self, quotes: List[PriceQuote]) -> float:
        """
        Calculate confidence score based on data quality factors.
        
        Factors:
        - Number of independent sources (0.4 weight)
        - Data freshness (0.3 weight)  
        - Price dispersion (0.2 weight)
        - Stock availability (0.1 weight)
        """
        if not quotes:
            return 0.0
        
        # Factor 1: Number of sources (0.4 weight)
        num_sources = len(quotes)
        source_score = min(num_sources / 5.0, 1.0)  # Max at 5 sources
        
        # Factor 2: Data freshness (0.3 weight)
        now = datetime.now()
        freshness_scores = []
        for quote in quotes:
            if quote.cached_at:
                # Ensure both datetimes have the same timezone awareness
                cached_time = quote.cached_at
                if cached_time.tzinfo is not None and now.tzinfo is None:
                    now = now.replace(tzinfo=cached_time.tzinfo)
                elif cached_time.tzinfo is None and now.tzinfo is not None:
                    cached_time = cached_time.replace(tzinfo=now.tzinfo)
                age_hours = (now - cached_time).total_seconds() / 3600
                # Score decreases linearly from 1.0 at 0 hours to 0.0 at 168 hours (1 week)
                freshness = max(0.0, 1.0 - (age_hours / 168.0))
                freshness_scores.append(freshness)
            else:
                freshness_scores.append(0.5)  # Unknown age gets medium score
        
        avg_freshness = sum(freshness_scores) / len(freshness_scores)
        
        # Factor 3: Price dispersion (0.2 weight)
        prices = [q.base_price for q in quotes if q.base_price > 0]
        if len(prices) > 1:
            mean_price = statistics.mean(prices)
            std_dev = statistics.stdev(prices)
            cv = std_dev / mean_price if mean_price > 0 else 1.0
            # Lower coefficient of variation = higher confidence
            dispersion_score = max(0.0, 1.0 - cv)
        else:
            dispersion_score = 0.5
        
        # Factor 4: Stock availability (0.1 weight)
        # Based on reliability scores if available
        reliability_scores = [q.reliability_score for q in quotes if q.reliability_score is not None]
        if reliability_scores:
            avg_reliability = sum(reliability_scores) / len(reliability_scores)
        else:
            avg_reliability = 0.7  # Default assumption
        
        # Weighted combination
        confidence = (
            source_score * 0.4 +
            avg_freshness * 0.3 +
            dispersion_score * 0.2 +
            avg_reliability * 0.1
        )
        
        return min(1.0, max(0.0, confidence))

    def analyze_product_specifications(self, product_input: ProductInput, quotes: List[PriceQuote]) -> ProductSpecAnalysis:
        """
        Analyze product specifications for canonical spec, purity, pack size.
        
        Requirements: 4.4
        """
        # Extract canonical specification from product name and specs
        canonical_spec = self._extract_canonical_spec(product_input)
        
        # Analyze purity grades from quotes
        purity_grades = [q.purity_grade for q in quotes if q.purity_grade]
        most_common_purity = max(set(purity_grades), key=purity_grades.count) if purity_grades else None
        
        # Analyze pack sizes
        pack_sizes = [q.pack_size for q in quotes if q.pack_size]
        most_common_pack = max(set(pack_sizes), key=pack_sizes.count) if pack_sizes else None
        
        # Find substitute SKUs (simplified - would use product database)
        substitute_skus = self._find_substitute_skus(product_input.name)
        
        # Calculate quality adjustment factor
        quality_adjustment = self._calculate_quality_adjustment(
            product_input, most_common_purity, most_common_pack
        )
        
        return ProductSpecAnalysis(
            canonical_spec=canonical_spec,
            purity_grade=most_common_purity,
            pack_size=most_common_pack,
            substitute_skus=substitute_skus,
            quality_adjustment=quality_adjustment
        )

    def evaluate_supplier_offers(self, quotes: List[PriceQuote], quantity: float) -> List[Dict[str, any]]:
        """
        Evaluate supplier offers including promotions, MOQ, price breaks.
        
        Requirements: 4.5
        """
        evaluations = []
        
        for quote in quotes:
            evaluation = {
                "supplier": quote.supplier,
                "base_price": quote.base_price,
                "effective_price": quote.base_price,
                "moq_met": True,
                "price_break_applied": False,
                "promotion_applied": False,
                "lead_time": quote.lead_time or 14,  # Default 2 weeks
                "reliability_score": quote.reliability_score or 0.7
            }
            
            # Check MOQ requirements
            if quote.moq and quantity < quote.moq:
                evaluation["moq_met"] = False
                evaluation["moq_shortfall"] = quote.moq - quantity
            
            # Apply price breaks if quantity qualifies
            if quote.price_breaks and evaluation["moq_met"]:
                applicable_breaks = {qty: price for qty, price in quote.price_breaks.items() if quantity >= qty}
                if applicable_breaks:
                    best_qty = max(applicable_breaks.keys())
                    evaluation["effective_price"] = applicable_breaks[best_qty]
                    evaluation["price_break_applied"] = True
                    evaluation["price_break_savings"] = quote.base_price - evaluation["effective_price"]
            
            # Factor in promotions (simplified)
            if quote.promotions:
                # Simple promotion parsing - would be more sophisticated in production
                if "10%" in quote.promotions.lower():
                    evaluation["effective_price"] *= 0.9
                    evaluation["promotion_applied"] = True
                elif "5%" in quote.promotions.lower():
                    evaluation["effective_price"] *= 0.95
                    evaluation["promotion_applied"] = True
            
            # Calculate value score (price vs reliability vs lead time)
            price_score = 1.0 / (evaluation["effective_price"] / min(q.base_price for q in quotes))
            reliability_score = evaluation["reliability_score"]
            lead_time_score = max(0.1, 1.0 - (evaluation["lead_time"] / 60.0))  # Penalty for long lead times
            
            evaluation["value_score"] = (price_score * 0.6 + reliability_score * 0.3 + lead_time_score * 0.1)
            
            evaluations.append(evaluation)
        
        # Sort by value score descending
        return sorted(evaluations, key=lambda x: x["value_score"], reverse=True)

    def calculate_location_factors(self, farm_location: FarmLocation, quotes: List[PriceQuote]) -> LocationFactors:
        """
        Calculate location-based cost factors.
        
        Requirements: 4.6
        """
        # Regional market density (simplified - would use real market data)
        state_density_factors = {
            "IA": 1.0, "IL": 1.0, "IN": 1.0, "NE": 0.95, "KS": 0.95,  # High ag density
            "CA": 1.1, "TX": 1.05, "FL": 1.1, "NY": 1.15,              # Mixed density
            "MT": 0.9, "WY": 0.9, "ND": 0.9, "SD": 0.9                 # Lower density
        }
        regional_density = state_density_factors.get(farm_location.state, 1.0)
        
        # Calculate average distance to suppliers (simplified)
        supplier_locations = [q.location for q in quotes if q.location]
        if supplier_locations:
            # Simplified distance calculation - would use real geocoding
            avg_distance = self._estimate_average_distance(farm_location, supplier_locations)
        else:
            avg_distance = 500.0  # Default assumption
        
        # Local competition level
        num_local_suppliers = sum(1 for q in quotes if q.location and self._is_local_supplier(farm_location, q.location))
        competition_level = min(1.1, 0.9 + (num_local_suppliers * 0.05))
        
        # Transportation infrastructure (simplified by state)
        infrastructure_factors = {
            "CA": 1.0, "TX": 1.0, "FL": 1.0, "IL": 1.0, "NY": 1.0,
            "IA": 0.98, "NE": 0.98, "KS": 0.98, "IN": 0.99,
            "MT": 0.95, "WY": 0.95, "AK": 0.9, "HI": 0.9
        }
        infrastructure = infrastructure_factors.get(farm_location.state, 0.98)
        
        return LocationFactors(
            regional_market_density=regional_density,
            distance_to_suppliers=avg_distance,
            local_competition_level=competition_level,
            transportation_infrastructure=infrastructure
        )

    def calculate_seasonality_factors(self, product_input: ProductInput) -> SeasonalityFactors:
        """
        Calculate seasonality factors for optimal timing.
        
        Requirements: 4.7
        """
        product_category = self._categorize_product(product_input.name)
        current_month = datetime.now().month
        
        # Get seasonal multipliers for this product category
        seasonal_data = self.seasonal_multipliers.get(product_category, {})
        if not seasonal_data:
            # Default seasonal pattern for unknown categories
            seasonal_data = {i: 1.0 for i in range(1, 13)}
        
        current_multiplier = seasonal_data.get(current_month, 1.0)
        
        # Find optimal purchase month (lowest multiplier)
        optimal_month = min(seasonal_data.keys(), key=lambda k: seasonal_data[k])
        optimal_multiplier = seasonal_data[optimal_month]
        
        # Calculate potential savings
        savings_potential = ((current_multiplier - optimal_multiplier) / current_multiplier) * 100
        
        # Planting calendar alignment (simplified)
        planting_months = self._get_planting_months(product_category)
        if current_month in planting_months:
            calendar_alignment = 1.1  # Premium for planting season
        elif current_month in [m - 1 for m in planting_months]:  # Month before planting
            calendar_alignment = 1.05
        else:
            calendar_alignment = 0.95
        
        return SeasonalityFactors(
            current_season_multiplier=current_multiplier,
            optimal_purchase_month=optimal_month,
            seasonal_savings_potential=max(0.0, savings_potential),
            planting_calendar_alignment=calendar_alignment
        )

    # Private helper methods
    
    def _normalize_to_base_uom(self, quote: PriceQuote, product_input: ProductInput) -> float:
        """Normalize price to base unit of measure"""
        # Simplified unit conversion - would use comprehensive conversion table
        unit_conversions = {
            ("lb", "kg"): 2.20462,
            ("kg", "lb"): 0.453592,
            ("gal", "l"): 3.78541,
            ("l", "gal"): 0.264172,
            ("oz", "g"): 28.3495,
            ("g", "oz"): 0.035274
        }
        
        conversion_key = (quote.unit.lower(), product_input.unit.lower())
        if conversion_key in unit_conversions:
            return quote.base_price * unit_conversions[conversion_key]
        
        return quote.base_price  # Assume same units if no conversion found

    def _calculate_logistics_cost(self, quote: PriceQuote, farm_location: FarmLocation) -> LogisticsCost:
        """Calculate detailed logistics costs"""
        # Simplified logistics calculation - would integrate with shipping APIs
        
        # Base freight estimate (per unit)
        base_freight = 2.50  # Default $2.50 per unit
        
        # Fuel surcharge (percentage of freight)
        fuel_surcharge = base_freight * 0.15
        
        # Handling fees
        handling_fees = 1.25
        
        # Delivery premium for remote locations
        remote_states = ["AK", "HI", "MT", "WY", "ND", "SD"]
        delivery_premium = 2.0 if farm_location.state in remote_states else 0.0
        
        total = base_freight + fuel_surcharge + handling_fees + delivery_premium
        
        return LogisticsCost(
            freight_estimate=base_freight,
            fuel_surcharge=fuel_surcharge,
            handling_fees=handling_fees,
            delivery_premium=delivery_premium,
            total=total
        )

    def _calculate_taxes_and_fees(self, quote: PriceQuote, farm_location: FarmLocation, base_price: float) -> TaxesAndFees:
        """Calculate taxes and regulatory fees"""
        # Sales tax
        tax_rate = self.state_tax_rates.get(farm_location.state, 0.06)
        sales_tax = base_price * tax_rate
        
        # Regulatory fees (simplified)
        regulatory_fees = 0.50  # Flat fee per unit
        
        # Certification costs (for organic/certified products)
        certification_costs = 0.25 if "organic" in quote.product_name.lower() else 0.0
        
        # Payment processing (2.9% for credit cards)
        payment_processing = base_price * 0.029
        
        total = sales_tax + regulatory_fees + certification_costs + payment_processing
        
        return TaxesAndFees(
            sales_tax=sales_tax,
            regulatory_fees=regulatory_fees,
            certification_costs=certification_costs,
            payment_processing=payment_processing,
            total=total
        )

    def _remove_outliers_mad(self, data: List[float], threshold: float = 2.5) -> List[float]:
        """Remove outliers using Median Absolute Deviation"""
        if len(data) < 3:
            return data
        
        median = statistics.median(data)
        mad = statistics.median([abs(x - median) for x in data])
        
        if mad == 0:
            return data
        
        # Modified Z-score
        modified_z_scores = [0.6745 * (x - median) / mad for x in data]
        
        return [data[i] for i, z in enumerate(modified_z_scores) if abs(z) < threshold]

    def _categorize_product(self, product_name: str) -> ProductCategory:
        """Categorize product based on name"""
        name_lower = product_name.lower()
        
        if any(word in name_lower for word in ["seed", "corn", "soybean", "wheat", "barley"]):
            return ProductCategory.SEEDS
        elif any(word in name_lower for word in ["fertilizer", "nitrogen", "phosphorus", "potash", "urea"]):
            return ProductCategory.FERTILIZER
        elif any(word in name_lower for word in ["pesticide", "herbicide", "insecticide", "fungicide"]):
            return ProductCategory.PESTICIDES
        elif any(word in name_lower for word in ["tractor", "plow", "harvester", "equipment"]):
            return ProductCategory.EQUIPMENT
        elif any(word in name_lower for word in ["fuel", "diesel", "gasoline", "propane"]):
            return ProductCategory.FUEL
        else:
            return ProductCategory.OTHER

    def _extract_canonical_spec(self, product_input: ProductInput) -> str:
        """Extract canonical product specification"""
        # Simplified - would use product database and NLP
        spec_parts = []
        
        # Add product name
        spec_parts.append(product_input.name.strip())
        
        # Add specifications if provided
        if product_input.specifications:
            spec_parts.append(product_input.specifications.strip())
        
        # Add unit
        spec_parts.append(f"per {product_input.unit}")
        
        return " | ".join(spec_parts)

    def _find_substitute_skus(self, product_name: str) -> List[str]:
        """Find substitute product SKUs"""
        # Simplified substitute mapping - would use product database
        substitutes_map = {
            "corn seed": ["hybrid corn", "gmo corn", "non-gmo corn"],
            "nitrogen fertilizer": ["urea", "ammonium nitrate", "liquid nitrogen"],
            "herbicide": ["glyphosate", "2,4-d", "atrazine"]
        }
        
        name_lower = product_name.lower()
        for key, subs in substitutes_map.items():
            if key in name_lower:
                return subs
        
        return []

    def _calculate_quality_adjustment(self, product_input: ProductInput, purity: Optional[str], pack_size: Optional[str]) -> float:
        """Calculate quality adjustment factor"""
        adjustment = 1.0
        
        # Purity adjustments
        if purity:
            if "premium" in purity.lower() or "99%" in purity:
                adjustment *= 1.05
            elif "standard" in purity.lower():
                adjustment *= 1.0
            elif "economy" in purity.lower():
                adjustment *= 0.95
        
        # Pack size efficiency
        if pack_size:
            if "bulk" in pack_size.lower() or "50lb" in pack_size or "25kg" in pack_size:
                adjustment *= 0.98  # Bulk discount
            elif "small" in pack_size.lower() or "5lb" in pack_size:
                adjustment *= 1.02  # Small pack premium
        
        return adjustment

    def _estimate_average_distance(self, farm_location: FarmLocation, supplier_locations: List[str]) -> float:
        """Estimate average distance to suppliers"""
        # Simplified distance estimation - would use geocoding API
        state_distances = {
            "CA": {"CA": 200, "NV": 300, "OR": 400, "AZ": 500},
            "TX": {"TX": 250, "OK": 300, "LA": 350, "NM": 400},
            "IL": {"IL": 150, "IN": 200, "IA": 250, "WI": 200}
        }
        
        farm_state = farm_location.state
        distances = []
        
        for supplier_loc in supplier_locations:
            # Extract state from supplier location (simplified)
            supplier_state = supplier_loc[-2:] if len(supplier_loc) >= 2 else farm_state
            
            if farm_state in state_distances and supplier_state in state_distances[farm_state]:
                distances.append(state_distances[farm_state][supplier_state])
            else:
                distances.append(400)  # Default distance
        
        return sum(distances) / len(distances) if distances else 400

    def _is_local_supplier(self, farm_location: FarmLocation, supplier_location: str) -> bool:
        """Check if supplier is local (same state)"""
        return farm_location.state in supplier_location

    def _get_planting_months(self, category: ProductCategory) -> List[int]:
        """Get typical planting months for product category"""
        planting_calendar = {
            ProductCategory.SEEDS: [3, 4, 5],      # March-May
            ProductCategory.FERTILIZER: [2, 3, 4], # Feb-April  
            ProductCategory.PESTICIDES: [4, 5, 6], # April-June
            ProductCategory.EQUIPMENT: [1, 2, 3],  # Jan-March
            ProductCategory.FUEL: list(range(1, 13)), # Year-round
            ProductCategory.OTHER: [3, 4, 5]       # Default spring
        }
        
        return planting_calendar.get(category, [3, 4, 5])

    def perform_comprehensive_economic_analysis(
        self, 
        product_input: ProductInput, 
        quotes: List[PriceQuote], 
        farm_location: FarmLocation
    ) -> Dict[str, Any]:
        """
        Perform comprehensive economic analysis combining all factors.
        
        This is the main analysis method that integrates:
        - Product specification analysis (Requirement 4.4)
        - Supplier offer evaluation (Requirement 4.5) 
        - Location factors (Requirement 4.6)
        - Seasonality factors (Requirement 4.7)
        """
        if not quotes:
            return {
                "error": "No price quotes available for analysis",
                "product_name": product_input.name,
                "analysis_complete": False
            }

        # 1. Product Specification Analysis (Requirement 4.4)
        spec_analysis = self.analyze_product_specifications(product_input, quotes)
        
        # 2. Supplier Offer Evaluation (Requirement 4.5)
        supplier_evaluations = self.evaluate_supplier_offers(quotes, product_input.quantity)
        
        # 3. Location Factors Analysis (Requirement 4.6)
        location_factors = self.calculate_location_factors(farm_location, quotes)
        
        # 4. Seasonality Analysis (Requirement 4.7)
        seasonality_factors = self.calculate_seasonality_factors(product_input)
        
        # 5. Calculate effective costs for all quotes
        effective_costs = []
        detailed_cost_breakdowns = []
        
        for quote in quotes:
            cost_breakdown = self.calculate_effective_delivered_cost(quote, farm_location, product_input)
            
            # Apply location and seasonality adjustments
            adjusted_cost = cost_breakdown["total_effective_cost"]
            adjusted_cost *= location_factors.regional_market_density
            adjusted_cost *= location_factors.local_competition_level  
            adjusted_cost *= location_factors.transportation_infrastructure
            adjusted_cost *= seasonality_factors.current_season_multiplier
            adjusted_cost *= seasonality_factors.planting_calendar_alignment
            adjusted_cost *= spec_analysis.quality_adjustment
            
            effective_costs.append(adjusted_cost)
            
            # Store detailed breakdown with adjustments
            cost_breakdown["location_adjustments"] = {
                "regional_density_factor": location_factors.regional_market_density,
                "competition_factor": location_factors.local_competition_level,
                "infrastructure_factor": location_factors.transportation_infrastructure
            }
            cost_breakdown["seasonality_adjustments"] = {
                "seasonal_multiplier": seasonality_factors.current_season_multiplier,
                "calendar_alignment": seasonality_factors.planting_calendar_alignment
            }
            cost_breakdown["quality_adjustment"] = spec_analysis.quality_adjustment
            cost_breakdown["final_adjusted_cost"] = adjusted_cost
            
            detailed_cost_breakdowns.append(cost_breakdown)
        
        # 6. Calculate statistical price ranges
        price_ranges = self.calculate_price_ranges(effective_costs)
        
        # 7. Calculate confidence score
        confidence_score = self.calculate_confidence_score(quotes)
        
        # 8. Generate market dynamics analysis
        market_dynamics = self._analyze_market_dynamics(quotes, effective_costs, seasonality_factors)
        
        # 9. Assess compliance and risk factors
        compliance_analysis = self._analyze_compliance_requirements(product_input, quotes, farm_location)
        
        # 10. Generate optimization recommendations
        optimization_recommendations = self._generate_optimization_recommendations(
            product_input, supplier_evaluations, seasonality_factors, 
            location_factors, spec_analysis, effective_costs
        )
        
        return {
            "product_name": product_input.name,
            "analysis_complete": True,
            "specification_analysis": {
                "canonical_spec": spec_analysis.canonical_spec,
                "purity_grade": spec_analysis.purity_grade,
                "pack_size": spec_analysis.pack_size,
                "substitute_skus": spec_analysis.substitute_skus,
                "quality_adjustment_factor": spec_analysis.quality_adjustment
            },
            "supplier_evaluations": supplier_evaluations,
            "location_factors": {
                "regional_market_density": location_factors.regional_market_density,
                "avg_distance_to_suppliers_km": location_factors.distance_to_suppliers,
                "local_competition_level": location_factors.local_competition_level,
                "transportation_infrastructure": location_factors.transportation_infrastructure
            },
            "seasonality_analysis": {
                "current_season_multiplier": seasonality_factors.current_season_multiplier,
                "optimal_purchase_month": seasonality_factors.optimal_purchase_month,
                "seasonal_savings_potential_pct": seasonality_factors.seasonal_savings_potential,
                "planting_calendar_alignment": seasonality_factors.planting_calendar_alignment
            },
            "price_analysis": {
                "price_ranges": {
                    "p10": price_ranges.p10,
                    "p25": price_ranges.p25,
                    "p35": price_ranges.p35,
                    "p50": price_ranges.p50,
                    "p90": price_ranges.p90
                },
                "target_price": price_ranges.p35,  # Target at p35 as per requirements
                "confidence_score": confidence_score,
                "num_quotes_analyzed": len(quotes)
            },
            "detailed_cost_breakdowns": detailed_cost_breakdowns,
            "market_dynamics": market_dynamics,
            "compliance_analysis": compliance_analysis,
            "optimization_recommendations": optimization_recommendations
        }

    def _analyze_market_dynamics(
        self, 
        quotes: List[PriceQuote], 
        effective_costs: List[float], 
        seasonality: SeasonalityFactors
    ) -> Dict[str, Any]:
        """
        Analyze market dynamics including price history, volatility, commodity linkage.
        
        Requirements: 4.5 (market dynamics analysis)
        """
        if not effective_costs:
            return {"analysis_available": False}
        
        # Price volatility analysis
        mean_price = statistics.mean(effective_costs)
        if len(effective_costs) > 1:
            price_volatility = statistics.stdev(effective_costs) / mean_price
        else:
            price_volatility = 0.0
        
        # Price trend analysis (simplified - would use historical data)
        sorted_prices = sorted(effective_costs)
        price_trend = "stable"
        if len(sorted_prices) >= 3:
            if sorted_prices[-1] > sorted_prices[0] * 1.1:
                price_trend = "increasing"
            elif sorted_prices[-1] < sorted_prices[0] * 0.9:
                price_trend = "decreasing"
        
        # Commodity linkage analysis (simplified)
        commodity_factors = self._analyze_commodity_linkage(quotes)
        
        # Supply chain risk assessment
        supply_risk = self._assess_supply_chain_risk(quotes)
        
        return {
            "analysis_available": True,
            "price_volatility": price_volatility,
            "volatility_level": "high" if price_volatility > 0.2 else "medium" if price_volatility > 0.1 else "low",
            "price_trend": price_trend,
            "mean_market_price": mean_price,
            "price_range_spread": max(effective_costs) - min(effective_costs) if effective_costs else 0,
            "commodity_linkage": commodity_factors,
            "supply_chain_risk": supply_risk,
            "seasonal_impact": {
                "current_vs_optimal": seasonality.current_season_multiplier / min(0.8, 1.0),
                "seasonal_volatility": seasonality.seasonal_savings_potential
            }
        }

    def _analyze_compliance_requirements(
        self, 
        product_input: ProductInput, 
        quotes: List[PriceQuote], 
        farm_location: FarmLocation
    ) -> Dict[str, Any]:
        """
        Analyze compliance requirements including regulatory status, certifications, taxes.
        
        Requirements: 4.6 (compliance requirements)
        """
        product_category = self._categorize_product(product_input.name)
        
        # Regulatory status analysis
        regulatory_requirements = self._get_regulatory_requirements(product_category, farm_location.state)
        
        # Certification analysis
        certification_analysis = self._analyze_certifications(product_input, quotes)
        
        # Tax implications
        tax_analysis = self._analyze_tax_implications(product_input, farm_location, quotes)
        
        # Payment terms analysis
        payment_terms = self._analyze_payment_terms(quotes)
        
        return {
            "regulatory_requirements": regulatory_requirements,
            "certification_analysis": certification_analysis,
            "tax_implications": tax_analysis,
            "payment_terms_analysis": payment_terms,
            "compliance_score": self._calculate_compliance_score(
                regulatory_requirements, certification_analysis, tax_analysis
            )
        }

    def _generate_optimization_recommendations(
        self,
        product_input: ProductInput,
        supplier_evaluations: List[Dict[str, Any]],
        seasonality: SeasonalityFactors,
        location: LocationFactors,
        spec_analysis: ProductSpecAnalysis,
        effective_costs: List[float]
    ) -> List[Dict[str, Any]]:
        """
        Generate comprehensive optimization recommendations.
        
        Combines insights from all analysis components to provide actionable recommendations.
        """
        recommendations = []
        
        # 1. Quantity optimization recommendations
        if supplier_evaluations:
            best_supplier = supplier_evaluations[0]  # Already sorted by value score
            
            if not best_supplier.get("moq_met", True):
                moq_shortfall = best_supplier.get("moq_shortfall", 0)
                recommendations.append({
                    "type": "QUANTITY_OPTIMIZATION",
                    "priority": "high",
                    "description": f"Increase quantity by {moq_shortfall} units to meet MOQ and unlock better pricing",
                    "potential_savings": best_supplier.get("price_break_savings", 0) * product_input.quantity,
                    "action_required": f"Consider ordering {moq_shortfall + product_input.quantity} units total",
                    "confidence": 0.9
                })
        
        # 2. Seasonal timing recommendations
        if seasonality.seasonal_savings_potential > 5.0:  # More than 5% savings potential
            recommendations.append({
                "type": "SEASONAL_TIMING",
                "priority": "medium",
                "description": f"Optimal purchase timing in month {seasonality.optimal_purchase_month} could save {seasonality.seasonal_savings_potential:.1f}%",
                "potential_savings": (sum(effective_costs) / len(effective_costs)) * (seasonality.seasonal_savings_potential / 100) * product_input.quantity,
                "action_required": f"Plan purchase for {self._month_name(seasonality.optimal_purchase_month)} if timing allows",
                "confidence": 0.8
            })
        
        # 3. Substitute product recommendations
        if spec_analysis.substitute_skus:
            recommendations.append({
                "type": "SUBSTITUTE_PRODUCTS",
                "priority": "low",
                "description": f"Consider substitute products: {', '.join(spec_analysis.substitute_skus[:3])}",
                "potential_savings": 0,  # Would need substitute pricing to calculate
                "action_required": "Research pricing for substitute products",
                "confidence": 0.6
            })
        
        # 4. Location-based recommendations
        if location.local_competition_level < 0.95:  # Low local competition
            recommendations.append({
                "type": "SUPPLIER_DIVERSIFICATION",
                "priority": "medium",
                "description": "Limited local competition detected - consider expanding supplier search radius",
                "potential_savings": 0,
                "action_required": "Search for suppliers in neighboring states or regions",
                "confidence": 0.7
            })
        
        # 5. Quality optimization recommendations
        if spec_analysis.quality_adjustment > 1.02:  # Premium quality premium
            recommendations.append({
                "type": "QUALITY_OPTIMIZATION",
                "priority": "low",
                "description": "Premium quality specifications may be adding unnecessary cost",
                "potential_savings": (sum(effective_costs) / len(effective_costs)) * 0.02 * product_input.quantity,
                "action_required": "Evaluate if standard grade meets requirements",
                "confidence": 0.6
            })
        
        return sorted(recommendations, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)

    # Additional helper methods for comprehensive analysis
    
    def _analyze_commodity_linkage(self, quotes: List[PriceQuote]) -> Dict[str, Any]:
        """Analyze linkage to commodity markets"""
        # Simplified commodity linkage analysis
        return {
            "linked_commodities": ["corn", "soybean", "wheat"],  # Would be product-specific
            "correlation_strength": 0.7,  # Would calculate from historical data
            "futures_impact": "moderate"
        }
    
    def _assess_supply_chain_risk(self, quotes: List[PriceQuote]) -> Dict[str, Any]:
        """Assess supply chain risk factors"""
        # Analyze supplier diversity
        unique_suppliers = len(set(q.supplier for q in quotes))
        supplier_diversity = min(1.0, unique_suppliers / 5.0)  # Normalize to 0-1
        
        # Analyze geographic diversity
        locations = [q.location for q in quotes if q.location]
        geographic_diversity = len(set(locations)) / max(1, len(locations))
        
        # Overall risk score (lower is better)
        risk_score = 1.0 - ((supplier_diversity + geographic_diversity) / 2.0)
        
        return {
            "supplier_diversity_score": supplier_diversity,
            "geographic_diversity_score": geographic_diversity,
            "overall_risk_score": risk_score,
            "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low"
        }
    
    def _get_regulatory_requirements(self, category: ProductCategory, state: str) -> Dict[str, Any]:
        """Get regulatory requirements by product category and state"""
        # Simplified regulatory requirements
        requirements = {
            ProductCategory.PESTICIDES: {
                "epa_registration": True,
                "state_licensing": True,
                "applicator_certification": True,
                "restricted_use": False  # Would check specific products
            },
            ProductCategory.FERTILIZER: {
                "nutrient_labeling": True,
                "state_registration": True,
                "organic_certification": False  # Product-specific
            },
            ProductCategory.SEEDS: {
                "variety_registration": True,
                "gmo_labeling": False,  # Product-specific
                "seed_certification": False
            }
        }
        
        return requirements.get(category, {"no_special_requirements": True})
    
    def _analyze_certifications(self, product_input: ProductInput, quotes: List[PriceQuote]) -> Dict[str, Any]:
        """Analyze certification requirements and availability"""
        # Check for organic requirements
        organic_required = "organic" in product_input.name.lower() or (
            product_input.specifications and "organic" in product_input.specifications.lower()
        )
        
        # Count organic suppliers
        organic_suppliers = sum(1 for q in quotes if "organic" in q.product_name.lower())
        
        return {
            "organic_required": organic_required,
            "organic_suppliers_available": organic_suppliers,
            "certification_premium": 0.15 if organic_required else 0.0,  # 15% premium for organic
            "other_certifications": []  # Would expand based on product type
        }
    
    def _analyze_tax_implications(self, product_input: ProductInput, farm_location: FarmLocation, quotes: List[PriceQuote]) -> Dict[str, Any]:
        """Analyze tax implications and exemptions"""
        # Agricultural exemptions (simplified)
        ag_exempt_states = ["IA", "IL", "IN", "NE", "KS", "MN", "WI"]
        has_ag_exemption = farm_location.state in ag_exempt_states
        
        base_tax_rate = self.state_tax_rates.get(farm_location.state, 0.06)
        effective_tax_rate = 0.0 if has_ag_exemption else base_tax_rate
        
        return {
            "base_tax_rate": base_tax_rate,
            "agricultural_exemption": has_ag_exemption,
            "effective_tax_rate": effective_tax_rate,
            "estimated_tax_savings": base_tax_rate * sum(q.base_price for q in quotes) * product_input.quantity if has_ag_exemption else 0
        }
    
    def _analyze_payment_terms(self, quotes: List[PriceQuote]) -> Dict[str, Any]:
        """Analyze payment terms and cash discount opportunities"""
        # Simplified payment terms analysis
        return {
            "cash_discount_available": True,  # Would parse from quote details
            "typical_cash_discount": 0.02,    # 2% for cash payment
            "net_terms_available": True,
            "typical_net_terms": 30           # Net 30 days
        }
    
    def _calculate_compliance_score(self, regulatory: Dict, certification: Dict, tax: Dict) -> float:
        """Calculate overall compliance score"""
        # Simplified compliance scoring
        score = 1.0
        
        # Penalty for complex regulatory requirements
        if regulatory.get("epa_registration") or regulatory.get("state_licensing"):
            score -= 0.1
        
        # Penalty for certification requirements
        if certification.get("organic_required"):
            score -= 0.05
        
        # Bonus for tax exemptions
        if tax.get("agricultural_exemption"):
            score += 0.05
        
        return max(0.0, min(1.0, score))
    
    def _month_name(self, month_num: int) -> str:
        """Convert month number to name"""
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        return months[month_num - 1] if 1 <= month_num <= 12 else "Unknown"