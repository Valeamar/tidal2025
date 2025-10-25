"""
Price Analysis Agent

This module implements the main AI agent that orchestrates comprehensive price analysis
for agricultural products by integrating market data service, price calculator, and AWS BI services.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
import uuid

from .models import (
    ProductInput, FarmLocation, PriceAnalysis, SupplierRecommendation,
    OptimizationRecommendation, EffectiveCost, IndividualBudget,
    DataAvailability, ProductAnalysisResult, ForecastResult,
    SentimentAnalysis, QuickSightInsights, AWSBIAnalysisResult,
    OptimizationType
)
from .market_data_service import MarketDataService, PriceQuote
from .price_calculator import PriceCalculator
from .aws_clients import get_aws_client_manager, AWSClientError, execute_aws_api_call
from .aws_bi_transforms import AWSBIDataTransformer
from .storage import MarketDataCache, StorageError
from .intelligent_recommendations import IntelligentRecommendationEngine, RecommendationValidator

logger = logging.getLogger(__name__)


class PriceAnalysisAgent:
    """
    Main AI agent that orchestrates comprehensive price analysis for agricultural products.
    
    Integrates:
    - Market data collection from multiple sources
    - Comprehensive economic analysis via price calculator
    - AWS BI services (Forecast, QuickSight, Comprehend) for intelligent insights
    - Individual product budget generation
    
    Requirements: 3.1, 3.6, 3.7
    """
    
    def __init__(self, use_mock_data: bool = True, enable_aws_bi: bool = False):
        """
        Initialize the Price Analysis Agent.
        
        Args:
            use_mock_data: Whether to use mock market data (for MVP)
            enable_aws_bi: Whether to enable AWS BI services integration
        """
        self.market_service = MarketDataService(use_mock_data=use_mock_data)
        self.calculator = PriceCalculator()
        self.cache = MarketDataCache()
        self.enable_aws_bi = enable_aws_bi
        self.recommendation_engine = IntelligentRecommendationEngine()
        
        # AWS BI clients (initialized only if enabled)
        self.aws_client_manager = None
        if enable_aws_bi:
            try:
                self.aws_client_manager = get_aws_client_manager()
                logger.info("AWS BI services enabled and initialized")
            except AWSClientError as e:
                logger.warning(f"AWS BI services disabled due to error: {e}")
                self.enable_aws_bi = False
        
        self.data_transformer = AWSBIDataTransformer()
        
        logger.info(f"PriceAnalysisAgent initialized (mock_data={use_mock_data}, aws_bi={self.enable_aws_bi})")
    
    async def analyze_product_list(
        self, 
        products: List[ProductInput], 
        farm_info: FarmLocation
    ) -> List[ProductAnalysisResult]:
        """
        Main analysis pipeline that processes a list of agricultural products.
        
        Integrates market data service, price calculator, and AWS BI services
        to generate comprehensive analysis and individual product budgets.
        
        Args:
            products: List of products to analyze
            farm_info: Farm location information for regional pricing
            
        Returns:
            List of ProductAnalysisResult objects with complete analysis
            
        Requirements: 3.1, 3.6, 3.7
        """
        logger.info(f"Starting analysis for {len(products)} products at {farm_info.city}, {farm_info.state}")
        
        results = []
        
        # Process each product individually
        for product in products:
            try:
                result = await self._analyze_single_product(product, farm_info)
                results.append(result)
                
                logger.info(f"Completed analysis for {product.name}")
                
            except Exception as e:
                logger.error(f"Error analyzing {product.name}: {e}")
                
                # Create error result with fallback data
                error_result = self._create_error_result(product, farm_info, str(e))
                results.append(error_result)
        
        logger.info(f"Analysis pipeline completed. {len(results)} results generated.")
        return results
    
    async def _analyze_single_product(
        self, 
        product: ProductInput, 
        farm_location: FarmLocation
    ) -> ProductAnalysisResult:
        """
        Analyze a single product with comprehensive economic analysis and AWS BI insights.
        
        Args:
            product: Product to analyze
            farm_location: Farm location for regional analysis
            
        Returns:
            Complete ProductAnalysisResult
        """
        product_id = str(uuid.uuid4())
        
        # Step 1: Get current market data
        logger.debug(f"Fetching market data for {product.name}")
        price_quotes = await self.market_service.get_current_prices(
            product.name, farm_location
        )
        
        # Step 2: Perform comprehensive economic analysis
        logger.debug(f"Performing economic analysis for {product.name}")
        economic_analysis = self.calculator.perform_comprehensive_economic_analysis(
            product, price_quotes, farm_location
        )
        
        # Step 3: Get AWS BI insights (if enabled)
        aws_bi_result = None
        if self.enable_aws_bi and price_quotes:
            logger.debug(f"Getting AWS BI insights for {product.name}")
            aws_bi_result = await self._get_aws_bi_insights(
                product.name, price_quotes, farm_location
            )
        
        # Step 4: Generate price analysis with AWS BI integration
        price_analysis = self._generate_price_analysis(
            product_id, product, economic_analysis, aws_bi_result, price_quotes, farm_location
        )
        
        # Step 5: Calculate individual product budget
        individual_budget = self._calculate_individual_budget(
            product, price_analysis.effective_delivered_cost
        )
        
        # Step 6: Assess data availability
        data_availability = self._assess_data_availability(
            price_quotes, aws_bi_result
        )
        
        return ProductAnalysisResult(
            product_id=product_id,
            product_name=product.name,
            analysis=price_analysis,
            individual_budget=individual_budget,
            data_availability=data_availability
        )
    
    async def _get_aws_bi_insights(
        self, 
        product_name: str, 
        price_quotes: List[PriceQuote],
        farm_location: FarmLocation
    ) -> Optional[AWSBIAnalysisResult]:
        """
        Get comprehensive AWS BI insights for a product.
        
        Integrates Amazon Forecast, QuickSight, and Comprehend services.
        
        Args:
            product_name: Name of the product
            price_quotes: Historical price quotes
            farm_location: Farm location for regional analysis
            
        Returns:
            AWSBIAnalysisResult or None if AWS BI is disabled/failed
        """
        if not self.enable_aws_bi or not self.aws_client_manager:
            return None
        
        start_time = datetime.now()
        services_used = []
        
        try:
            # Get forecast insights
            forecast_result = await self._get_forecast_insights(product_name, price_quotes)
            if forecast_result:
                services_used.append('forecast')
            
            # Get sentiment analysis
            sentiment_analysis = await self._get_sentiment_analysis(product_name)
            if sentiment_analysis:
                services_used.append('comprehend')
            
            # Get QuickSight insights
            quicksight_insights = await self._get_quicksight_insights(
                product_name, price_quotes, farm_location
            )
            if quicksight_insights:
                services_used.append('quicksight')
            
            # Calculate confidence factors
            data_completeness = len(price_quotes) / 10.0  # Normalize to 0-1 scale
            confidence_factors, overall_confidence = self.data_transformer.calculate_aws_bi_confidence(
                forecast_result, sentiment_analysis, quicksight_insights, data_completeness
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AWSBIAnalysisResult(
                product_name=product_name,
                forecast_result=forecast_result,
                sentiment_analysis=sentiment_analysis,
                quicksight_insights=quicksight_insights,
                confidence_factors=confidence_factors,
                overall_bi_confidence=overall_confidence,
                analysis_timestamp=datetime.now(),
                aws_services_used=services_used,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"AWS BI analysis failed for {product_name}: {e}")
            return None
    
    async def _get_forecast_insights(
        self, 
        product_name: str, 
        price_quotes: List[PriceQuote]
    ) -> Optional[ForecastResult]:
        """
        Get Amazon Forecast price predictions.
        
        Args:
            product_name: Product name
            price_quotes: Historical price data
            
        Returns:
            ForecastResult or None if forecast unavailable
        """
        try:
            if len(price_quotes) < 10:  # Need sufficient historical data
                logger.debug(f"Insufficient data for forecast: {len(price_quotes)} quotes")
                return None
            
            # Transform data for Forecast service
            forecast_dataset = self.data_transformer.price_quotes_to_forecast_dataset(
                price_quotes, product_name
            )
            
            if not forecast_dataset:
                return None
            
            # For MVP: Generate mock forecast result
            # In production, this would call actual Amazon Forecast API
            mock_forecast_response = self._generate_mock_forecast_response(
                product_name, price_quotes
            )
            
            return self.data_transformer.transform_forecast_response(
                mock_forecast_response, product_name
            )
            
        except Exception as e:
            logger.error(f"Forecast analysis failed for {product_name}: {e}")
            return None
    
    async def _get_sentiment_analysis(self, product_name: str) -> Optional[SentimentAnalysis]:
        """
        Get AWS Comprehend sentiment analysis for market conditions.
        
        Args:
            product_name: Product name for market news analysis
            
        Returns:
            SentimentAnalysis or None if analysis unavailable
        """
        try:
            # For MVP: Generate mock sentiment analysis
            # In production, this would analyze real market news with Comprehend
            mock_sentiment_response = self._generate_mock_sentiment_response(product_name)
            
            return self.data_transformer.transform_comprehend_response(
                mock_sentiment_response, product_name
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed for {product_name}: {e}")
            return None
    
    async def _get_quicksight_insights(
        self, 
        product_name: str, 
        price_quotes: List[PriceQuote],
        farm_location: FarmLocation
    ) -> Optional[QuickSightInsights]:
        """
        Get AWS QuickSight ML insights and analytics.
        
        Args:
            product_name: Product name
            price_quotes: Price data for analysis
            farm_location: Farm location for regional insights
            
        Returns:
            QuickSightInsights or None if insights unavailable
        """
        try:
            # For MVP: Generate mock QuickSight insights
            # In production, this would use real QuickSight ML insights
            mock_insights = self._generate_mock_quicksight_insights(
                product_name, price_quotes
            )
            
            return mock_insights
            
        except Exception as e:
            logger.error(f"QuickSight insights failed for {product_name}: {e}")
            return None
    
    def _generate_price_analysis(
        self, 
        product_id: str,
        product: ProductInput,
        economic_analysis: Dict[str, Any],
        aws_bi_result: Optional[AWSBIAnalysisResult],
        price_quotes: List[PriceQuote],
        farm_location: FarmLocation
    ) -> PriceAnalysis:
        """
        Generate comprehensive price analysis combining economic analysis and AWS BI insights.
        
        Args:
            product_id: Unique product identifier
            product: Product input information
            economic_analysis: Results from price calculator
            aws_bi_result: AWS BI analysis results
            
        Returns:
            Complete PriceAnalysis object
        """
        # Extract price ranges from economic analysis
        price_ranges = economic_analysis.get("price_analysis", {}).get("price_ranges", {})
        effective_cost = EffectiveCost(
            p10=price_ranges.get("p10"),
            p25=price_ranges.get("p25"),
            p35=price_ranges.get("p35"),
            p50=price_ranges.get("p50"),
            p90=price_ranges.get("p90")
        )
        
        # Generate supplier recommendations
        supplier_recommendations = self._generate_supplier_recommendations(
            economic_analysis.get("supplier_evaluations", [])
        )
        
        # Generate comprehensive optimization recommendations using intelligent engine
        market_data_quality = self._assess_market_data_quality(price_quotes)
        optimization_recommendations = self.recommendation_engine.generate_comprehensive_recommendations(
            product, farm_location, aws_bi_result, market_data_quality, economic_analysis
        )
        
        # Calculate confidence score (enhanced with AWS BI)
        confidence_score = self._calculate_enhanced_confidence_score(
            economic_analysis.get("price_analysis", {}).get("confidence_score", 0.5),
            aws_bi_result
        )
        
        # Identify data limitations
        data_limitations = self._identify_data_limitations(
            economic_analysis, aws_bi_result
        )
        
        return PriceAnalysis(
            product_id=product_id,
            product_name=product.name,
            effective_delivered_cost=effective_cost,
            target_price=price_ranges.get("p35"),  # Target at p35 as per requirements
            confidence_score=confidence_score,
            suppliers=supplier_recommendations,
            recommendations=optimization_recommendations,
            data_limitations=data_limitations
        )
    
    def _calculate_individual_budget(
        self, 
        product: ProductInput, 
        effective_cost: EffectiveCost
    ) -> IndividualBudget:
        """
        Calculate individual product budget based on price analysis.
        
        Args:
            product: Product input with quantity information
            effective_cost: Effective cost analysis results
            
        Returns:
            IndividualBudget with cost projections
        """
        quantity = product.quantity
        
        # Use price ranges to calculate budget scenarios
        low_cost = (effective_cost.p10 or 0) * quantity
        target_cost = (effective_cost.p35 or effective_cost.p25 or 0) * quantity
        high_cost = (effective_cost.p90 or 0) * quantity
        
        # Use target cost as total cost estimate
        total_cost = target_cost
        
        return IndividualBudget(
            low=low_cost,
            target=target_cost,
            high=high_cost,
            total_cost=total_cost
        )
    
    def _assess_data_availability(
        self, 
        price_quotes: List[PriceQuote],
        aws_bi_result: Optional[AWSBIAnalysisResult]
    ) -> DataAvailability:
        """
        Assess data availability and quality for the analysis.
        
        Args:
            price_quotes: Market price quotes
            aws_bi_result: AWS BI analysis results
            
        Returns:
            DataAvailability assessment
        """
        price_data_found = len(price_quotes) > 0
        supplier_data_found = any(quote.supplier for quote in price_quotes)
        
        # AWS BI data availability
        forecast_available = bool(
            aws_bi_result and 
            aws_bi_result.forecast_result and 
            len(aws_bi_result.forecast_result.predictions) > 0
        )
        
        sentiment_available = bool(
            aws_bi_result and 
            aws_bi_result.sentiment_analysis is not None
        )
        
        # Identify missing data sections
        missing_sections = []
        if not price_data_found:
            missing_sections.append("Market price data")
        if not supplier_data_found:
            missing_sections.append("Supplier information")
        if not forecast_available:
            missing_sections.append("Price forecast data")
        if not sentiment_available:
            missing_sections.append("Market sentiment data")
        
        return DataAvailability(
            price_data_found=price_data_found,
            supplier_data_found=supplier_data_found,
            forecast_data_available=forecast_available,
            sentiment_data_available=sentiment_available,
            missing_data_sections=missing_sections
        )
    
    def _generate_supplier_recommendations(
        self, 
        supplier_evaluations: List[Dict[str, Any]]
    ) -> List[SupplierRecommendation]:
        """
        Generate supplier recommendations from economic analysis.
        
        Args:
            supplier_evaluations: Supplier evaluation results
            
        Returns:
            List of SupplierRecommendation objects
        """
        recommendations = []
        
        # Take top 3 suppliers by value score
        for eval_data in supplier_evaluations[:3]:
            recommendation = SupplierRecommendation(
                name=eval_data.get("supplier", "Unknown"),
                price=eval_data.get("effective_price", 0.0),
                delivery_terms=None,  # Would be extracted from quote data
                lead_time=eval_data.get("lead_time"),
                reliability=eval_data.get("reliability_score"),
                moq=None,  # Would be extracted from quote data
                contact_info=None,  # Would be extracted from quote data
                location=None  # Would be extracted from quote data
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _assess_market_data_quality(self, price_quotes: List[PriceQuote]) -> Dict[str, Any]:

        """
        Assess market data quality for recommendation engine.
        
        Args:
            price_quotes: List of price quotes
            
        Returns:
            Dictionary with data quality metrics
        """
        if not price_quotes:
            return {
                "overall_score": 0.0,
                "quote_count": 0,
                "supplier_data_found": False,
                "source_diversity": 0,
                "reliability_score": 0.0,
                "freshness_score": 0.0
            }
        
        # Calculate quality metrics
        quote_count = len(price_quotes)
        unique_sources = len(set(quote.supplier for quote in price_quotes))
        supplier_data_found = any(quote.supplier for quote in price_quotes)
        
        # Average reliability
        reliabilities = [quote.reliability_score for quote in price_quotes if quote.reliability_score]
        avg_reliability = sum(reliabilities) / len(reliabilities) if reliabilities else 0.5
        
        # Data freshness
        now = datetime.now(timezone.utc)
        freshness_scores = []
        for quote in price_quotes:
            if quote.cached_at:
                # Ensure both datetimes are timezone-aware
                cached_time = quote.cached_at
                if cached_time.tzinfo is None:
                    cached_time = cached_time.replace(tzinfo=timezone.utc)
                hours_old = (now - cached_time).total_seconds() / 3600
                if hours_old < 1:
                    freshness_scores.append(1.0)
                elif hours_old < 6:
                    freshness_scores.append(0.8)
                elif hours_old < 24:
                    freshness_scores.append(0.6)
                else:
                    freshness_scores.append(0.3)
            else:
                freshness_scores.append(0.5)
        
        avg_freshness = sum(freshness_scores) / len(freshness_scores)
        
        # Overall score calculation
        source_score = min(unique_sources / 3.0, 1.0)
        overall_score = (
            source_score * 0.3 +
            avg_reliability * 0.3 +
            avg_freshness * 0.2 +
            (1.0 if supplier_data_found else 0.0) * 0.2
        )
        
        return {
            "overall_score": overall_score,
            "quote_count": quote_count,
            "supplier_data_found": supplier_data_found,
            "source_diversity": unique_sources,
            "reliability_score": avg_reliability,
            "freshness_score": avg_freshness
        }
    

    
    def _calculate_enhanced_confidence_score(
        self, 
        base_confidence: float,
        aws_bi_result: Optional[AWSBIAnalysisResult]
    ) -> float:
        """
        Calculate enhanced confidence score incorporating AWS BI insights.
        
        Args:
            base_confidence: Base confidence from economic analysis
            aws_bi_result: AWS BI analysis results
            
        Returns:
            Enhanced confidence score (0.0 to 1.0)
        """
        if not aws_bi_result:
            return base_confidence
        
        # Weight base confidence at 60%, AWS BI confidence at 40%
        enhanced_confidence = (
            base_confidence * 0.6 + 
            aws_bi_result.overall_bi_confidence * 0.4
        )
        
        return min(1.0, max(0.0, enhanced_confidence))
    
    def _identify_data_limitations(
        self, 
        economic_analysis: Dict[str, Any],
        aws_bi_result: Optional[AWSBIAnalysisResult]
    ) -> List[str]:
        """
        Identify data limitations from both economic analysis and AWS BI results.
        
        Args:
            economic_analysis: Economic analysis results
            aws_bi_result: AWS BI analysis results
            
        Returns:
            List of data limitation descriptions
        """
        limitations = []
        
        # Check quote count
        num_quotes = economic_analysis.get("price_analysis", {}).get("num_quotes_analyzed", 0)
        if num_quotes == 0:
            limitations.append("No market price data available")
        elif num_quotes < 3:
            limitations.append(f"Limited market data: only {num_quotes} price quote(s)")
        
        # Check AWS BI data limitations
        if aws_bi_result:
            if not aws_bi_result.forecast_result:
                limitations.append("Price forecast data unavailable")
            elif len(aws_bi_result.forecast_result.predictions) < 5:
                limitations.append("Limited forecast horizon due to insufficient historical data")
            
            if not aws_bi_result.sentiment_analysis:
                limitations.append("Market sentiment analysis unavailable")
            elif aws_bi_result.sentiment_analysis.news_sources_analyzed < 3:
                limitations.append("Limited market sentiment data sources")
            
            if not aws_bi_result.quicksight_insights:
                limitations.append("Advanced analytics insights unavailable")
        else:
            limitations.append("AWS BI services not available - analysis based on basic market data only")
        
        # Check confidence factors
        confidence = economic_analysis.get("price_analysis", {}).get("confidence_score", 0)
        if confidence < 0.5:
            limitations.append("Low confidence in price estimates due to data quality issues")
        
        return limitations
    
    def _create_error_result(
        self, 
        product: ProductInput, 
        farm_location: FarmLocation,
        error_message: str
    ) -> ProductAnalysisResult:
        """
        Create error result when analysis fails.
        
        Args:
            product: Product that failed analysis
            farm_location: Farm location
            error_message: Error description
            
        Returns:
            ProductAnalysisResult with error information
        """
        product_id = str(uuid.uuid4())
        
        # Create minimal analysis with error information
        error_analysis = PriceAnalysis(
            product_id=product_id,
            product_name=product.name,
            effective_delivered_cost=EffectiveCost(),
            target_price=None,
            confidence_score=0.0,
            suppliers=[],
            recommendations=[],
            data_limitations=[
                "Analysis failed due to technical error",
                f"Error: {error_message}",
                "Manual research required for this product"
            ]
        )
        
        # Create zero budget
        error_budget = IndividualBudget(
            low=0.0,
            target=0.0,
            high=0.0,
            total_cost=0.0
        )
        
        # Create data availability with all false
        error_availability = DataAvailability(
            price_data_found=False,
            supplier_data_found=False,
            forecast_data_available=False,
            sentiment_data_available=False,
            missing_data_sections=["All data sources unavailable due to error"]
        )
        
        return ProductAnalysisResult(
            product_id=product_id,
            product_name=product.name,
            analysis=error_analysis,
            individual_budget=error_budget,
            data_availability=error_availability
        )
    
    # Mock data generation methods for MVP (will be replaced with real AWS API calls)
    
    def _generate_mock_forecast_response(
        self, 
        product_name: str, 
        price_quotes: List[PriceQuote]
    ) -> Dict[str, Any]:
        """Generate mock Amazon Forecast response for MVP testing."""
        if not price_quotes:
            return {}
        
        base_price = sum(q.base_price for q in price_quotes) / len(price_quotes)
        
        # Generate 30-day forecast with slight trend
        predictions = []
        for i in range(30):
            date = (datetime.now() + timedelta(days=i)).isoformat()
            # Add slight downward trend for demonstration
            trend_factor = 1.0 - (i * 0.001)  # 0.1% decline per day
            predicted_price = base_price * trend_factor
            
            predictions.append({
                'Timestamp': date,
                'Value': predicted_price,
                'LowerBound': predicted_price * 0.9,
                'UpperBound': predicted_price * 1.1
            })
        
        return {
            'Forecast': {
                'Predictions': {
                    'p50': predictions
                }
            },
            'Confidence': 0.8,
            'DataQualityScore': 0.75
        }
    
    def _generate_mock_sentiment_response(self, product_name: str) -> Dict[str, Any]:
        """Generate mock AWS Comprehend sentiment response for MVP testing."""
        # Simulate neutral to slightly positive sentiment for agricultural products
        return {
            'SentimentResult': {
                'Sentiment': 'NEUTRAL',
                'SentimentScore': {
                    'Positive': 0.3,
                    'Negative': 0.2,
                    'Neutral': 0.5,
                    'Mixed': 0.0
                }
            },
            'Entities': [
                {
                    'Text': 'weather conditions',
                    'Type': 'OTHER',
                    'Score': 0.8
                },
                {
                    'Text': 'supply chain',
                    'Type': 'OTHER', 
                    'Score': 0.7
                }
            ],
            'SourceDocuments': ['mock_news_1', 'mock_news_2', 'mock_news_3']
        }
    
    def _generate_mock_quicksight_insights(
        self, 
        product_name: str, 
        price_quotes: List[PriceQuote]
    ) -> QuickSightInsights:
        """Generate mock QuickSight insights for MVP testing."""
        # Simulate seasonal pattern detection
        current_month = datetime.now().month
        optimal_month = 2 if current_month > 2 else 11  # February or November
        
        return QuickSightInsights(
            price_anomaly_detected=False,
            seasonal_pattern_detected=True,
            optimal_purchase_month=f"Month {optimal_month}",
            seasonal_savings_potential=8.5,  # 8.5% potential savings
            pattern_confidence=0.75,
            trend_analysis=TrendAnalysis(
                direction="stable",
                strength=0.6,
                duration_days=30,
                statistical_significance=0.8
            ),
            correlations=[
                CorrelationFactor(
                    factor="fuel_prices",
                    correlation_strength=0.6,
                    impact_description="Moderate positive correlation with fuel costs"
                )
            ],
            insights_generated_at=datetime.now(),
            data_freshness_score=0.8
        )


# Import required models for mock data generation
from datetime import timedelta
from .models import TrendAnalysis, CorrelationFactor