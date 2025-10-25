"""
Intelligent Recommendations System

This module implements AWS BI-powered recommendation generation with comprehensive
data availability checks and fallback strategies for the Farmer Budget Optimizer.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from .models import (
    ProductInput, FarmLocation, OptimizationRecommendation, OptimizationType,
    ForecastResult, SentimentAnalysis, QuickSightInsights, AWSBIAnalysisResult
)

logger = logging.getLogger(__name__)


class RecommendationPriority(str, Enum):
    """Priority levels for recommendations"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationCategory(str, Enum):
    """Categories of recommendations"""
    TIMING = "timing"
    QUANTITY = "quantity"
    SUPPLIER = "supplier"
    RISK_MANAGEMENT = "risk_management"
    COST_OPTIMIZATION = "cost_optimization"
    MARKET_INTELLIGENCE = "market_intelligence"


class IntelligentRecommendationEngine:
    """
    Advanced recommendation engine that generates intelligent, data-driven recommendations
    using AWS BI services with comprehensive fallback strategies.
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
    """
    
    def __init__(self):
        """Initialize the intelligent recommendation engine."""
        self.confidence_thresholds = {
            RecommendationPriority.CRITICAL: 0.9,
            RecommendationPriority.HIGH: 0.8,
            RecommendationPriority.MEDIUM: 0.6,
            RecommendationPriority.LOW: 0.4
        }
        
        logger.info("IntelligentRecommendationEngine initialized")
    
    def generate_comprehensive_recommendations(
        self,
        product: ProductInput,
        farm_location: FarmLocation,
        aws_bi_result: Optional[AWSBIAnalysisResult],
        market_data_quality: Dict[str, Any],
        economic_analysis: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """
        Generate comprehensive recommendations using all available data sources.
        
        Args:
            product: Product information
            farm_location: Farm location for regional analysis
            aws_bi_result: AWS BI analysis results (may be None)
            market_data_quality: Market data quality assessment
            economic_analysis: Economic analysis results
            
        Returns:
            List of prioritized OptimizationRecommendation objects
            
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
        """
        logger.info(f"Generating comprehensive recommendations for {product.name}")
        
        all_recommendations = []
        
        # 1. AWS BI-powered recommendations (if available)
        if aws_bi_result:
            aws_recommendations = self._generate_aws_bi_recommendations(
                product, aws_bi_result, farm_location
            )
            all_recommendations.extend(aws_recommendations)
        
        # 2. Timing-based recommendations
        timing_recommendations = self._generate_timing_recommendations(
            product, aws_bi_result, economic_analysis
        )
        all_recommendations.extend(timing_recommendations)
        
        # 3. Bulk discount and quantity optimization
        quantity_recommendations = self._generate_quantity_recommendations(
            product, economic_analysis, market_data_quality
        )
        all_recommendations.extend(quantity_recommendations)
        
        # 4. Seasonal optimization recommendations
        seasonal_recommendations = self._generate_seasonal_recommendations(
            product, aws_bi_result, economic_analysis
        )
        all_recommendations.extend(seasonal_recommendations)
        
        # 5. Supply risk and anomaly alerts
        risk_recommendations = self._generate_risk_recommendations(
            product, aws_bi_result, market_data_quality
        )
        all_recommendations.extend(risk_recommendations)
        
        # 6. Inventory management strategies
        inventory_recommendations = self._generate_inventory_management_recommendations(
            product, aws_bi_result, economic_analysis, farm_location
        )
        all_recommendations.extend(inventory_recommendations)
        
        # 7. Alternative recommendations for limited data
        if not aws_bi_result or market_data_quality.get("overall_score", 0) < 0.5:
            fallback_recommendations = self._generate_fallback_recommendations(
                product, market_data_quality, economic_analysis
            )
            all_recommendations.extend(fallback_recommendations)
        
        # 7. Prioritize and filter recommendations
        prioritized_recommendations = self._prioritize_recommendations(all_recommendations)
        
        logger.info(f"Generated {len(prioritized_recommendations)} recommendations for {product.name}")
        return prioritized_recommendations[:8]  # Return top 8 recommendations
    
    def _generate_aws_bi_recommendations(
        self,
        product: ProductInput,
        aws_bi_result: AWSBIAnalysisResult,
        farm_location: FarmLocation
    ) -> List[OptimizationRecommendation]:
        """
        Generate recommendations based on AWS BI insights with data availability checks.
        
        Requirements: 5.1, 5.2, 5.3
        """
        recommendations = []
        
        # Amazon Forecast-based recommendations
        if aws_bi_result.forecast_result:
            forecast_recs = self._generate_forecast_recommendations(
                product, aws_bi_result.forecast_result
            )
            recommendations.extend(forecast_recs)
        
        # AWS Comprehend sentiment-based recommendations
        if aws_bi_result.sentiment_analysis:
            sentiment_recs = self._generate_sentiment_recommendations(
                product, aws_bi_result.sentiment_analysis
            )
            recommendations.extend(sentiment_recs)
        
        # QuickSight ML insights recommendations
        if aws_bi_result.quicksight_insights:
            quicksight_recs = self._generate_quicksight_recommendations(
                product, aws_bi_result.quicksight_insights
            )
            recommendations.extend(quicksight_recs)
        
        return recommendations
    
    def _generate_forecast_recommendations(
        self,
        product: ProductInput,
        forecast_result: ForecastResult
    ) -> List[OptimizationRecommendation]:
        """
        Generate recommendations based on Amazon Forecast price predictions.
        
        Requirements: 5.1 (timing recommendations based on forecast data)
        """
        recommendations = []
        
        if not forecast_result.predictions or forecast_result.confidence < 0.6:
            return recommendations
        
        current_price = forecast_result.predictions[0].predicted_price
        
        # Declining price recommendations
        if forecast_result.trend == "declining" and forecast_result.decline_percentage > 3:
            if forecast_result.lowest_price_date and forecast_result.predicted_lowest_price:
                savings_per_unit = current_price - forecast_result.predicted_lowest_price
                total_savings = savings_per_unit * product.quantity
                
                recommendations.append(OptimizationRecommendation(
                    type=OptimizationType.TIMING,
                    description=f"Amazon Forecast predicts {forecast_result.decline_percentage:.1f}% price decline by {forecast_result.lowest_price_date}",
                    potential_savings=total_savings,
                    action_required=f"Delay purchase until {forecast_result.lowest_price_date} for optimal pricing",
                    confidence=forecast_result.confidence
                ))
        
        # Rising price recommendations
        elif forecast_result.trend == "increasing":
            # Find steepest price increase period
            steepest_increase = self._find_steepest_price_increase(forecast_result.predictions)
            if steepest_increase:
                recommendations.append(OptimizationRecommendation(
                    type=OptimizationType.TIMING,
                    description=f"Forecast shows prices rising {steepest_increase['rate']:.1f}% over next {steepest_increase['days']} days",
                    potential_savings=steepest_increase['avoided_cost'] * product.quantity,
                    action_required="Consider purchasing immediately to avoid price increases",
                    confidence=forecast_result.confidence
                ))
        
        # Seasonality-based recommendations
        if forecast_result.seasonality_detected:
            seasonal_rec = self._generate_seasonality_forecast_recommendation(
                product, forecast_result
            )
            if seasonal_rec:
                recommendations.append(seasonal_rec)
        
        return recommendations
    
    def _generate_sentiment_recommendations(
        self,
        product: ProductInput,
        sentiment_analysis: SentimentAnalysis
    ) -> List[OptimizationRecommendation]:
        """
        Generate recommendations based on AWS Comprehend market sentiment analysis.
        
        Requirements: 5.3, 5.4 (supply risk and anomaly alerts based on market sentiment)
        """
        recommendations = []
        
        # High supply risk recommendations
        if sentiment_analysis.supply_risk_score > 0.7:
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.SUPPLY_RISK,
                description=f"Market sentiment indicates {sentiment_analysis.risk_level} supply risk for {product.name}",
                potential_savings=0.0,  # Risk mitigation rather than savings
                action_required="Secure inventory early or identify alternative suppliers to mitigate supply disruption risk",
                confidence=sentiment_analysis.confidence_score
            ))
        
        # Strong demand outlook recommendations
        if sentiment_analysis.demand_outlook == "Strong" and sentiment_analysis.overall_sentiment == "POSITIVE":
            estimated_price_impact = product.quantity * (product.max_price or 100) * 0.05  # 5% price increase estimate
            
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.TIMING,
                description=f"Strong market demand detected - prices likely to increase due to {sentiment_analysis.overall_sentiment.lower()} sentiment",
                potential_savings=estimated_price_impact,
                action_required="Consider accelerating purchase timeline before demand-driven price increases",
                confidence=sentiment_analysis.confidence_score
            ))
        
        # Weak demand recommendations
        elif sentiment_analysis.demand_outlook == "Weak" and sentiment_analysis.overall_sentiment == "NEGATIVE":
            estimated_savings = product.quantity * (product.max_price or 100) * 0.03  # 3% savings estimate
            
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.TIMING,
                description=f"Weak demand outlook suggests potential for price negotiations",
                potential_savings=estimated_savings,
                action_required="Negotiate with suppliers for better pricing due to weak market conditions",
                confidence=sentiment_analysis.confidence_score
            ))
        
        # Key factor-based recommendations
        for factor in sentiment_analysis.key_factors:
            if factor.confidence > 0.7:
                factor_rec = self._generate_factor_based_recommendation(
                    product, factor, sentiment_analysis
                )
                if factor_rec:
                    recommendations.append(factor_rec)
        
        return recommendations
    
    def _generate_quicksight_recommendations(
        self,
        product: ProductInput,
        quicksight_insights: QuickSightInsights
    ) -> List[OptimizationRecommendation]:
        """
        Generate recommendations based on AWS QuickSight ML insights.
        
        Requirements: 5.2, 5.6 (anomaly detection and pattern recognition)
        """
        recommendations = []
        
        # Price anomaly recommendations
        if quicksight_insights.price_anomaly_detected and quicksight_insights.anomaly_confidence:
            if quicksight_insights.anomaly_confidence > 0.7:
                recommendations.append(OptimizationRecommendation(
                    type=OptimizationType.ANOMALY_ALERT,
                    description=f"Price anomaly detected: {quicksight_insights.anomaly_description}",
                    potential_savings=0.0,
                    action_required="Investigate unusual market conditions and consider delaying purchase until market stabilizes",
                    confidence=quicksight_insights.anomaly_confidence
                ))
        
        # Seasonal pattern recommendations
        if (quicksight_insights.seasonal_pattern_detected and 
            quicksight_insights.seasonal_savings_potential and
            quicksight_insights.seasonal_savings_potential > 5.0):
            
            savings_amount = product.quantity * (product.max_price or 100) * (quicksight_insights.seasonal_savings_potential / 100)
            
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.SEASONAL_OPTIMIZATION,
                description=f"Seasonal analysis shows {quicksight_insights.seasonal_savings_potential:.1f}% savings opportunity in {quicksight_insights.optimal_purchase_month}",
                potential_savings=savings_amount,
                action_required=f"Plan purchase for {quicksight_insights.optimal_purchase_month} if operational timing allows",
                confidence=quicksight_insights.pattern_confidence or 0.8
            ))
        
        # Correlation-based recommendations
        for correlation in quicksight_insights.correlations:
            if abs(correlation.correlation_strength) > 0.6:  # Strong correlation
                corr_rec = self._generate_correlation_recommendation(
                    product, correlation, quicksight_insights
                )
                if corr_rec:
                    recommendations.append(corr_rec)
        
        # Trend-based recommendations
        if quicksight_insights.trend_analysis:
            trend_rec = self._generate_trend_recommendation(
                product, quicksight_insights.trend_analysis
            )
            if trend_rec:
                recommendations.append(trend_rec)
        
        return recommendations
    
    def _generate_timing_recommendations(
        self,
        product: ProductInput,
        aws_bi_result: Optional[AWSBIAnalysisResult],
        economic_analysis: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """
        Generate timing recommendations based on available forecast data.
        
        Requirements: 5.1 (timing recommendations based on available forecast data)
        """
        recommendations = []
        
        # Get seasonality factors from economic analysis
        seasonality = economic_analysis.get("seasonality_analysis", {})
        
        if seasonality.get("seasonal_savings_potential_pct", 0) > 5:
            optimal_month = seasonality.get("optimal_purchase_month")
            savings_pct = seasonality.get("seasonal_savings_potential_pct")
            
            if optimal_month and savings_pct:
                estimated_savings = product.quantity * (product.max_price or 100) * (savings_pct / 100)
                
                recommendations.append(OptimizationRecommendation(
                    type=OptimizationType.SEASONAL_OPTIMIZATION,
                    description=f"Historical data shows {savings_pct:.1f}% lower prices in month {optimal_month}",
                    potential_savings=estimated_savings,
                    action_required=f"Consider timing purchase for month {optimal_month} if operationally feasible",
                    confidence=0.7  # Historical data confidence
                ))
        
        return recommendations
    
    def _generate_quantity_recommendations(
        self,
        product: ProductInput,
        economic_analysis: Dict[str, Any],
        market_data_quality: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """
        Generate bulk discount and quantity optimization recommendations.
        
        Requirements: 5.5 (bulk discount suggestions when supplier data exists)
        """
        recommendations = []
        
        # Check supplier evaluations for MOQ and price break opportunities
        supplier_evaluations = economic_analysis.get("supplier_evaluations", [])
        
        for supplier_eval in supplier_evaluations[:3]:  # Top 3 suppliers
            # MOQ recommendations
            if not supplier_eval.get("moq_met", True):
                moq_shortfall = supplier_eval.get("moq_shortfall", 0)
                if moq_shortfall > 0:
                    # Calculate potential savings from meeting MOQ
                    price_break_savings = supplier_eval.get("price_break_savings", 0)
                    total_savings = price_break_savings * (product.quantity + moq_shortfall)
                    
                    recommendations.append(OptimizationRecommendation(
                        type=OptimizationType.BULK_DISCOUNT,
                        description=f"Increase quantity by {moq_shortfall} units to meet {supplier_eval['supplier']} MOQ and unlock bulk pricing",
                        potential_savings=total_savings,
                        action_required=f"Consider ordering {product.quantity + moq_shortfall} total units from {supplier_eval['supplier']}",
                        confidence=0.9 if market_data_quality.get("supplier_data_found", False) else 0.6
                    ))
            
            # Price break recommendations
            elif supplier_eval.get("price_break_applied", False):
                price_break_savings = supplier_eval.get("price_break_savings", 0)
                if price_break_savings > 0:
                    recommendations.append(OptimizationRecommendation(
                        type=OptimizationType.BULK_DISCOUNT,
                        description=f"Current quantity qualifies for bulk pricing with {supplier_eval['supplier']} (${price_break_savings:.2f} per unit savings)",
                        potential_savings=price_break_savings * product.quantity,
                        action_required=f"Confirm bulk pricing terms with {supplier_eval['supplier']}",
                        confidence=0.8
                    ))
        
        return recommendations
    
    def _generate_seasonal_recommendations(
        self,
        product: ProductInput,
        aws_bi_result: Optional[AWSBIAnalysisResult],
        economic_analysis: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """
        Generate seasonal optimization suggestions when supplier data exists.
        
        Requirements: 5.5 (seasonal optimization suggestions when supplier data exists)
        """
        recommendations = []
        
        # Use AWS BI seasonal data if available, otherwise fall back to economic analysis
        if aws_bi_result and aws_bi_result.quicksight_insights:
            insights = aws_bi_result.quicksight_insights
            if insights.seasonal_pattern_detected and insights.seasonal_savings_potential:
                if insights.seasonal_savings_potential > 3.0:  # Minimum 3% savings threshold
                    savings_amount = product.quantity * (product.max_price or 100) * (insights.seasonal_savings_potential / 100)
                    
                    recommendations.append(OptimizationRecommendation(
                        type=OptimizationType.SEASONAL_OPTIMIZATION,
                        description=f"ML analysis identifies {insights.seasonal_savings_potential:.1f}% seasonal savings in {insights.optimal_purchase_month}",
                        potential_savings=savings_amount,
                        action_required=f"Align purchase timing with {insights.optimal_purchase_month} seasonal low",
                        confidence=insights.pattern_confidence or 0.8
                    ))
        
        # Fallback to economic analysis seasonality
        else:
            seasonality = economic_analysis.get("seasonality_analysis", {})
            current_multiplier = seasonality.get("current_season_multiplier", 1.0)
            
            if current_multiplier > 1.05:  # Currently in high-price season
                optimal_month = seasonality.get("optimal_purchase_month")
                savings_potential = seasonality.get("seasonal_savings_potential_pct", 0)
                
                if optimal_month and savings_potential > 3:
                    estimated_savings = product.quantity * (product.max_price or 100) * (savings_potential / 100)
                    
                    recommendations.append(OptimizationRecommendation(
                        type=OptimizationType.SEASONAL_OPTIMIZATION,
                        description=f"Currently in high-price season (multiplier: {current_multiplier:.2f}). Historical data shows {savings_potential:.1f}% savings in month {optimal_month}",
                        potential_savings=estimated_savings,
                        action_required=f"Consider delaying purchase until month {optimal_month} if timing permits",
                        confidence=0.7
                    ))
        
        return recommendations
    
    def _generate_inventory_management_recommendations(
        self,
        product: ProductInput,
        aws_bi_result: Optional[AWSBIAnalysisResult],
        economic_analysis: Dict[str, Any],
        farm_location: FarmLocation
    ) -> List[OptimizationRecommendation]:
        """
        Generate inventory management strategies including optimal storage timing and quantities.
        
        Requirements: 5.7 (inventory management strategies including optimal storage timing and quantities)
        """
        recommendations = []
        
        # Storage timing recommendations based on seasonality
        seasonality = economic_analysis.get("seasonality_analysis", {})
        current_month = datetime.now().month
        
        # Recommend early storage for seasonal products
        if seasonality.get("seasonal_savings_potential_pct", 0) > 10:
            optimal_month = seasonality.get("optimal_purchase_month", current_month)
            
            # If we're approaching optimal purchase month
            months_to_optimal = (optimal_month - current_month) % 12
            if months_to_optimal <= 2 and months_to_optimal > 0:
                storage_savings = product.quantity * (product.max_price or 100) * 0.08  # 8% storage savings
                
                recommendations.append(OptimizationRecommendation(
                    type=OptimizationType.SEASONAL_OPTIMIZATION,
                    description=f"Optimal purchase window approaching in {months_to_optimal} month(s) - consider storage capacity",
                    potential_savings=storage_savings,
                    action_required=f"Prepare storage facilities for bulk purchase in month {optimal_month}",
                    confidence=0.8
                ))
        
        # Quantity optimization for storage efficiency
        if product.quantity > 1000:  # Large quantity threshold
            # Recommend splitting large orders for better storage management
            split_savings = product.quantity * (product.max_price or 100) * 0.02  # 2% efficiency savings
            
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.BULK_DISCOUNT,
                description=f"Large quantity ({product.quantity} units) may benefit from staged delivery",
                potential_savings=split_savings,
                action_required="Consider splitting order into 2-3 deliveries to optimize storage costs and cash flow",
                confidence=0.7
            ))
        
        # Storage cost vs. price volatility analysis
        if aws_bi_result and aws_bi_result.forecast_result:
            forecast = aws_bi_result.forecast_result
            if forecast.trend == "increasing" and len(forecast.predictions) > 30:
                # Calculate storage cost vs. price increase
                current_price = forecast.predictions[0].predicted_price
                future_price = forecast.predictions[30].predicted_price  # 30 days out
                
                price_increase = ((future_price - current_price) / current_price) * 100
                if price_increase > 5:  # More than 5% increase expected
                    storage_value = (future_price - current_price) * product.quantity
                    
                    recommendations.append(OptimizationRecommendation(
                        type=OptimizationType.TIMING,
                        description=f"Price forecast shows {price_increase:.1f}% increase over 30 days - storage may be profitable",
                        potential_savings=storage_value * 0.7,  # Account for storage costs
                        action_required="Evaluate storage costs vs. projected price increases for inventory buildup",
                        confidence=forecast.confidence
                    ))
        
        # Shelf life and spoilage considerations
        if any(term in product.name.lower() for term in ['seed', 'fertilizer', 'chemical']):
            # Products with limited shelf life
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.TIMING,
                description="Product has limited shelf life - optimize purchase timing with usage schedule",
                potential_savings=0.0,
                action_required="Align purchase timing with planting schedule to minimize spoilage risk",
                confidence=0.9
            ))
        
        return recommendations
   
    def _generate_risk_recommendations(
        self,
        product: ProductInput,
        aws_bi_result: Optional[AWSBIAnalysisResult],
        market_data_quality: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """
        Generate supply risk and anomaly alerts based on available market sentiment.
        
        Requirements: 5.3, 5.4 (supply risk and anomaly alerts based on available market sentiment)
        """
        recommendations = []
        
        # AWS BI-based risk recommendations
        if aws_bi_result:
            # Sentiment-based supply risk
            if aws_bi_result.sentiment_analysis:
                sentiment = aws_bi_result.sentiment_analysis
                if sentiment.supply_risk_score > 0.6:
                    recommendations.append(OptimizationRecommendation(
                        type=OptimizationType.SUPPLY_RISK,
                        description=f"Market sentiment analysis indicates {sentiment.risk_level} supply risk",
                        potential_savings=0.0,
                        action_required="Diversify suppliers and consider early inventory securing",
                        confidence=sentiment.confidence_score
                    ))
            
            # QuickSight anomaly alerts
            if aws_bi_result.quicksight_insights and aws_bi_result.quicksight_insights.price_anomaly_detected:
                insights = aws_bi_result.quicksight_insights
                recommendations.append(OptimizationRecommendation(
                    type=OptimizationType.ANOMALY_ALERT,
                    description=f"Price anomaly detected: {insights.anomaly_description}",
                    potential_savings=0.0,
                    action_required="Monitor market conditions closely before making purchase decisions",
                    confidence=insights.anomaly_confidence or 0.7
                ))
        
        # Market data quality-based risk recommendations
        data_coverage = market_data_quality.get("overall_score", 0)
        if data_coverage < 0.4:
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.SUPPLY_RISK,
                description=f"Low market data coverage ({data_coverage:.1%}) increases purchase risk",
                potential_savings=0.0,
                action_required="Conduct additional market research and get multiple quotes before purchasing",
                confidence=0.8
            ))
        
        # Supplier diversity risk
        quote_count = market_data_quality.get("quote_count", 0)
        if quote_count < 3:
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.SUPPLY_RISK,
                description=f"Limited supplier options ({quote_count} quotes) increases supply risk",
                potential_savings=0.0,
                action_required="Expand supplier search to reduce dependency risk",
                confidence=0.7
            ))
        
        return recommendations
    
    def _generate_fallback_recommendations(
        self,
        product: ProductInput,
        market_data_quality: Dict[str, Any],
        economic_analysis: Dict[str, Any]
    ) -> List[OptimizationRecommendation]:
        """
        Provide alternative recommendations when primary data sources are unavailable.
        
        Requirements: 5.7 (alternative recommendations when primary data sources unavailable)
        """
        recommendations = []
        
        # Manual research recommendations for low data availability
        if market_data_quality.get("overall_score", 0) < 0.3:
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.SUBSTITUTE,
                description="Limited market data available - manual research recommended",
                potential_savings=0.0,
                action_required="Contact local suppliers directly for current pricing and availability",
                confidence=0.9
            ))
        
        # Regional supplier recommendations
        if not market_data_quality.get("supplier_data_found", False):
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.SUBSTITUTE,
                description="No supplier contact information found in market data",
                potential_savings=0.0,
                action_required="Research regional agricultural suppliers and cooperatives",
                confidence=0.8
            ))
        
        # Enhanced group purchasing recommendations (Requirement 5.4)
        if product.quantity < 500:  # Expanded threshold for group purchasing
            # Calculate potential group purchase benefits
            group_discount_rate = 0.08 if product.quantity < 100 else 0.05  # Higher discount for smaller quantities
            estimated_savings = product.quantity * (product.max_price or 100) * group_discount_rate
            
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.GROUP_PURCHASE,
                description=f"Quantity ({product.quantity} units) qualifies for {group_discount_rate*100:.0f}% group purchasing discount",
                potential_savings=estimated_savings,
                action_required="Contact local farm cooperatives or organize group purchase with neighboring farms",
                confidence=0.7
            ))
            
            # Regional cooperative recommendations
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.GROUP_PURCHASE,
                description="Regional farm cooperatives may offer volume discounts and shared logistics",
                potential_savings=estimated_savings * 1.2,  # Additional logistics savings
                action_required="Research regional agricultural cooperatives and buying groups in your area",
                confidence=0.6
            ))
        
        # Conservative timing recommendations
        current_month = datetime.now().month
        if current_month in [3, 4, 5]:  # Spring planting season
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.TIMING,
                description="Currently in peak planting season - prices typically higher",
                potential_savings=0.0,
                action_required="Consider if purchase can be delayed to off-season for better pricing",
                confidence=0.6
            ))
        
        # Enhanced substitute product recommendations (Requirement 5.5)
        if product.specifications and "premium" in product.specifications.lower():
            estimated_savings = product.quantity * (product.max_price or 100) * 0.12  # 12% premium reduction
            
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.SUBSTITUTE,
                description="Premium grade may be substitutable with standard grade for significant savings",
                potential_savings=estimated_savings,
                action_required="Compare premium vs. standard grade specifications against actual crop requirements",
                confidence=0.7
            ))
        
        # Generic vs. brand name substitutions
        if product.preferred_brands and len(product.preferred_brands) > 0:
            brand_savings = product.quantity * (product.max_price or 100) * 0.15  # 15% brand premium
            
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.SUBSTITUTE,
                description="Generic alternatives may offer equivalent performance at lower cost",
                potential_savings=brand_savings,
                action_required="Research generic or store-brand alternatives with similar active ingredients",
                confidence=0.6
            ))
        
        # Product category substitutions
        product_lower = product.name.lower()
        if "fertilizer" in product_lower:
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.SUBSTITUTE,
                description="Consider alternative fertilizer formulations or organic options",
                potential_savings=product.quantity * (product.max_price or 100) * 0.08,
                action_required="Evaluate liquid vs. granular fertilizers or organic alternatives for cost savings",
                confidence=0.5
            ))
        elif "seed" in product_lower:
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.SUBSTITUTE,
                description="Alternative seed varieties may offer better value or performance",
                potential_savings=product.quantity * (product.max_price or 100) * 0.06,
                action_required="Compare different seed varieties for yield potential vs. cost",
                confidence=0.6
            ))
        
        return recommendations
    
    def _prioritize_recommendations(
        self,
        recommendations: List[OptimizationRecommendation]
    ) -> List[OptimizationRecommendation]:
        """
        Prioritize recommendations based on potential savings, confidence, and urgency.
        
        Args:
            recommendations: List of recommendations to prioritize
            
        Returns:
            Sorted list of recommendations by priority
        """
        def calculate_priority_score(rec: OptimizationRecommendation) -> float:
            """Calculate priority score for sorting."""
            # Base score from potential savings (normalized)
            savings_score = min(rec.potential_savings / 1000.0, 1.0)  # Normalize to 0-1
            
            # Confidence weight
            confidence_weight = rec.confidence or 0.5
            
            # Type-based urgency multiplier
            urgency_multipliers = {
                OptimizationType.SUPPLY_RISK: 1.5,
                OptimizationType.ANOMALY_ALERT: 1.4,
                OptimizationType.TIMING: 1.3,
                OptimizationType.BULK_DISCOUNT: 1.2,
                OptimizationType.SEASONAL_OPTIMIZATION: 1.1,
                OptimizationType.GROUP_PURCHASE: 1.0,
                OptimizationType.SUBSTITUTE: 0.9
            }
            
            urgency = urgency_multipliers.get(rec.type, 1.0)
            
            # Combined priority score
            return (savings_score * 0.4 + confidence_weight * 0.4 + urgency * 0.2)
        
        # Sort by priority score (descending)
        prioritized = sorted(
            recommendations,
            key=calculate_priority_score,
            reverse=True
        )
        
        return prioritized
    
    # Helper methods for specific recommendation types
    
    def _find_steepest_price_increase(
        self,
        predictions: List[Any]
    ) -> Optional[Dict[str, Any]]:
        """Find the steepest price increase period in forecast predictions."""
        if len(predictions) < 7:  # Need at least a week of data
            return None
        
        max_increase_rate = 0
        best_period = None
        
        for i in range(len(predictions) - 6):  # 7-day windows
            start_price = predictions[i].predicted_price
            end_price = predictions[i + 6].predicted_price
            
            if start_price > 0:
                increase_rate = ((end_price - start_price) / start_price) * 100
                
                if increase_rate > max_increase_rate and increase_rate > 2:  # Minimum 2% increase
                    max_increase_rate = increase_rate
                    best_period = {
                        'rate': increase_rate,
                        'days': 7,
                        'avoided_cost': end_price - start_price
                    }
        
        return best_period
    
    def _generate_seasonality_forecast_recommendation(
        self,
        product: ProductInput,
        forecast_result: ForecastResult
    ) -> Optional[OptimizationRecommendation]:
        """Generate seasonality recommendation from forecast data."""
        if not forecast_result.predictions or len(forecast_result.predictions) < 30:
            return None
        
        # Find lowest price in forecast period
        min_price = min(p.predicted_price for p in forecast_result.predictions)
        min_price_prediction = next(p for p in forecast_result.predictions if p.predicted_price == min_price)
        current_price = forecast_result.predictions[0].predicted_price
        
        if (current_price - min_price) / current_price > 0.05:  # More than 5% savings
            savings = (current_price - min_price) * product.quantity
            
            return OptimizationRecommendation(
                type=OptimizationType.SEASONAL_OPTIMIZATION,
                description=f"Forecast shows seasonal low of ${min_price:.2f} on {min_price_prediction.date}",
                potential_savings=savings,
                action_required=f"Consider timing purchase for {min_price_prediction.date}",
                confidence=forecast_result.confidence
            )
        
        return None
    
    def _generate_factor_based_recommendation(
        self,
        product: ProductInput,
        factor: Any,  # SentimentFactor
        sentiment_analysis: SentimentAnalysis
    ) -> Optional[OptimizationRecommendation]:
        """Generate recommendation based on specific sentiment factors."""
        factor_name = factor.factor.lower()
        
        # Weather-related recommendations
        if "weather" in factor_name:
            if factor.sentiment == "NEGATIVE":
                return OptimizationRecommendation(
                    type=OptimizationType.SUPPLY_RISK,
                    description=f"Negative weather sentiment detected - potential supply disruption risk",
                    potential_savings=0.0,
                    action_required="Monitor weather conditions and consider early purchasing",
                    confidence=factor.confidence
                )
        
        # Supply chain recommendations
        elif "supply" in factor_name or "logistics" in factor_name:
            if factor.sentiment == "NEGATIVE":
                return OptimizationRecommendation(
                    type=OptimizationType.SUPPLY_RISK,
                    description=f"Supply chain concerns detected in market sentiment",
                    potential_savings=0.0,
                    action_required="Secure alternative suppliers and delivery options",
                    confidence=factor.confidence
                )
        
        return None
    
    def _generate_correlation_recommendation(
        self,
        product: ProductInput,
        correlation: Any,  # CorrelationFactor
        quicksight_insights: QuickSightInsights
    ) -> Optional[OptimizationRecommendation]:
        """Generate recommendation based on correlation analysis."""
        factor_name = correlation.factor.lower()
        
        # Fuel price correlation
        if "fuel" in factor_name and abs(correlation.correlation_strength) > 0.7:
            return OptimizationRecommendation(
                type=OptimizationType.TIMING,
                description=f"Strong correlation with fuel prices detected ({correlation.correlation_strength:.2f})",
                potential_savings=0.0,
                action_required="Monitor fuel price trends for optimal purchase timing",
                confidence=0.7
            )
        
        # Weather correlation
        elif "weather" in factor_name and correlation.correlation_strength > 0.6:
            return OptimizationRecommendation(
                type=OptimizationType.TIMING,
                description=f"Price correlation with weather patterns identified",
                potential_savings=0.0,
                action_required="Consider weather forecasts in purchase timing decisions",
                confidence=0.6
            )
        
        return None
    
    def _generate_trend_recommendation(
        self,
        product: ProductInput,
        trend_analysis: Any  # TrendAnalysis
    ) -> Optional[OptimizationRecommendation]:
        """Generate recommendation based on trend analysis."""
        if trend_analysis.statistical_significance < 0.6:
            return None
        
        if trend_analysis.direction == "increasing" and trend_analysis.strength > 0.7:
            return OptimizationRecommendation(
                type=OptimizationType.TIMING,
                description=f"Strong upward price trend detected (strength: {trend_analysis.strength:.2f})",
                potential_savings=0.0,
                action_required="Consider purchasing soon to avoid further price increases",
                confidence=trend_analysis.statistical_significance
            )
        
        elif trend_analysis.direction == "decreasing" and trend_analysis.strength > 0.7:
            estimated_savings = product.quantity * (product.max_price or 100) * 0.03  # 3% estimate
            
            return OptimizationRecommendation(
                type=OptimizationType.TIMING,
                description=f"Strong downward price trend detected (strength: {trend_analysis.strength:.2f})",
                potential_savings=estimated_savings,
                action_required="Consider delaying purchase to benefit from declining prices",
                confidence=trend_analysis.statistical_significance
            )
        
        return None


class RecommendationValidator:
    """
    Validates and filters recommendations to ensure quality and relevance.
    """
    
    @staticmethod
    def validate_recommendations(
        recommendations: List[OptimizationRecommendation],
        product: ProductInput,
        constraints: Optional[Dict[str, Any]] = None
    ) -> List[OptimizationRecommendation]:
        """
        Validate and filter recommendations based on business rules and constraints.
        
        Args:
            recommendations: List of recommendations to validate
            product: Product information for context
            constraints: Optional constraints (timing, budget, etc.)
            
        Returns:
            Filtered list of valid recommendations
        """
        valid_recommendations = []
        constraints = constraints or {}
        
        for rec in recommendations:
            # Basic validation
            if not rec.description or not rec.action_required:
                continue
            
            # Confidence threshold
            if (rec.confidence or 0) < 0.3:
                continue
            
            # Timing constraints
            if constraints.get("urgent_purchase") and rec.type == OptimizationType.TIMING:
                if "delay" in rec.action_required.lower():
                    continue  # Skip delay recommendations for urgent purchases
            
            # Budget constraints
            max_budget = constraints.get("max_budget")
            if max_budget and rec.type == OptimizationType.BULK_DISCOUNT:
                # Check if bulk purchase exceeds budget
                current_cost = product.quantity * (product.max_price or 100)
                if current_cost > max_budget:
                    continue
            
            # Seasonal constraints
            if constraints.get("immediate_need") and rec.type == OptimizationType.SEASONAL_OPTIMIZATION:
                if "month" in rec.action_required.lower():
                    continue  # Skip seasonal timing for immediate needs
            
            valid_recommendations.append(rec)
        
        return valid_recommendations


class RecommendationFormatter:
    """
    Formats recommendations for different output formats and user interfaces.
    """
    
    @staticmethod
    def format_for_api_response(
        recommendations: List[OptimizationRecommendation]
    ) -> List[Dict[str, Any]]:
        """
        Format recommendations for API response.
        
        Args:
            recommendations: List of recommendations to format
            
        Returns:
            List of formatted recommendation dictionaries
        """
        formatted = []
        
        for i, rec in enumerate(recommendations):
            formatted_rec = {
                "id": i + 1,
                "type": rec.type.value,
                "priority": RecommendationFormatter._determine_priority(rec),
                "title": RecommendationFormatter._generate_title(rec),
                "description": rec.description,
                "action_required": rec.action_required,
                "potential_savings": rec.potential_savings,
                "confidence_score": rec.confidence or 0.5,
                "confidence_level": RecommendationFormatter._confidence_to_level(rec.confidence or 0.5),
                "urgency": RecommendationFormatter._determine_urgency(rec),
                "implementation_difficulty": RecommendationFormatter._assess_difficulty(rec)
            }
            formatted.append(formatted_rec)
        
        return formatted
    
    @staticmethod
    def _determine_priority(rec: OptimizationRecommendation) -> str:
        """Determine priority level for recommendation."""
        if rec.potential_savings > 500 or rec.type in [OptimizationType.SUPPLY_RISK, OptimizationType.ANOMALY_ALERT]:
            return "high"
        elif rec.potential_savings > 100 or (rec.confidence or 0) > 0.8:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def _generate_title(rec: OptimizationRecommendation) -> str:
        """Generate concise title for recommendation."""
        type_titles = {
            OptimizationType.TIMING: "Optimal Purchase Timing",
            OptimizationType.BULK_DISCOUNT: "Bulk Purchase Opportunity",
            OptimizationType.SEASONAL_OPTIMIZATION: "Seasonal Price Optimization",
            OptimizationType.SUPPLY_RISK: "Supply Risk Alert",
            OptimizationType.ANOMALY_ALERT: "Market Anomaly Alert",
            OptimizationType.GROUP_PURCHASE: "Group Purchase Opportunity",
            OptimizationType.SUBSTITUTE: "Alternative Product Option"
        }
        return type_titles.get(rec.type, "Optimization Opportunity")
    
    @staticmethod
    def _confidence_to_level(confidence: float) -> str:
        """Convert confidence score to level."""
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.6:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def _determine_urgency(rec: OptimizationRecommendation) -> str:
        """Determine urgency level."""
        if rec.type in [OptimizationType.SUPPLY_RISK, OptimizationType.ANOMALY_ALERT]:
            return "urgent"
        elif rec.type == OptimizationType.TIMING and "soon" in rec.action_required.lower():
            return "high"
        else:
            return "normal"
    
    @staticmethod
    def _assess_difficulty(rec: OptimizationRecommendation) -> str:
        """Assess implementation difficulty."""
        if rec.type in [OptimizationType.SUBSTITUTE, OptimizationType.GROUP_PURCHASE]:
            return "high"
        elif rec.type in [OptimizationType.BULK_DISCOUNT, OptimizationType.TIMING]:
            return "medium"
        else:
            return "low"