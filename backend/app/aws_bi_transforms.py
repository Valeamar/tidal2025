"""
AWS BI Data Transformation Functions

This module provides data transformation functions for converting between
application data models and AWS service input/output formats.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from .models import (
    PriceQuote, ForecastResult, SentimentAnalysis, QuickSightInsights,
    ForecastDatasetInput, ComprehendTextInput, QuickSightDataInput,
    ForecastPrediction, SentimentFactor, CorrelationFactor, TrendAnalysis,
    AWSBIConfidenceFactors, AWSBIAnalysisResult
)


class AWSBIDataTransformer:
    """
    Handles data transformations between application models and AWS BI services.
    """
    
    @staticmethod
    def price_quotes_to_forecast_dataset(
        price_quotes: List[PriceQuote], 
        product_name: str
    ) -> List[ForecastDatasetInput]:
        """
        Transform price quotes to Amazon Forecast dataset format.
        
        Args:
            price_quotes: List of price quotes with timestamps
            product_name: Product identifier for the dataset
            
        Returns:
            List of ForecastDatasetInput objects
        """
        dataset_inputs = []
        
        for quote in price_quotes:
            if quote.cached_at:
                dataset_inputs.append(ForecastDatasetInput(
                    timestamp=quote.cached_at.isoformat(),
                    target_value=quote.base_price,
                    item_id=product_name.lower().replace(' ', '_'),
                    location=quote.location,
                    category=AWSBIDataTransformer._categorize_product(product_name)
                ))
        
        # Sort by timestamp for proper time series format
        dataset_inputs.sort(key=lambda x: x.timestamp)
        return dataset_inputs
    
    @staticmethod
    def _categorize_product(product_name: str) -> str:
        """
        Categorize product for better forecast modeling.
        
        Args:
            product_name: Name of the product
            
        Returns:
            Product category string
        """
        product_lower = product_name.lower()
        
        if any(term in product_lower for term in ['seed', 'corn', 'soy', 'wheat']):
            return 'seeds'
        elif any(term in product_lower for term in ['fertilizer', 'nitrogen', 'phosphorus']):
            return 'fertilizers'
        elif any(term in product_lower for term in ['pesticide', 'herbicide', 'insecticide']):
            return 'chemicals'
        elif any(term in product_lower for term in ['fuel', 'diesel', 'gas']):
            return 'fuel'
        else:
            return 'other'
    
    @staticmethod
    def create_market_news_inputs(
        product_name: str, 
        news_articles: List[Dict[str, Any]]
    ) -> List[ComprehendTextInput]:
        """
        Create Comprehend input from market news articles.
        
        Args:
            product_name: Product name for context
            news_articles: List of news article dictionaries
            
        Returns:
            List of ComprehendTextInput objects
        """
        comprehend_inputs = []
        
        for article in news_articles:
            # Combine title and content for analysis
            text_content = f"{article.get('title', '')} {article.get('content', '')}"
            
            if len(text_content.strip()) > 10:  # Minimum content check
                comprehend_inputs.append(ComprehendTextInput(
                    text=text_content[:5000],  # Truncate to max length
                    language_code="en",
                    source_url=article.get('url'),
                    publication_date=article.get('published_date'),
                    source_type=article.get('source_type', 'news')
                ))
        
        return comprehend_inputs
    
    @staticmethod
    def transform_forecast_response(
        aws_response: Dict[str, Any], 
        product_name: str
    ) -> ForecastResult:
        """
        Transform Amazon Forecast API response to ForecastResult model.
        
        Following AWS best practices for data validation and error handling.
        
        Args:
            aws_response: Raw AWS Forecast API response
            product_name: Product name for context
            
        Returns:
            ForecastResult object
            
        Raises:
            ValueError: If response format is invalid
        """
        if not aws_response:
            raise ValueError("Empty AWS Forecast response")
        
        predictions = []
        
        # AWS best practice: Validate response structure before processing
        forecast_data = aws_response.get('Forecast', {})
        if not forecast_data:
            # Handle case where no forecast data is available
            return ForecastResult(
                predictions=[],
                trend='stable',
                confidence=0.0,
                forecast_horizon_days=0,
                data_quality_score=0.0
            )
        
        predictions_raw = forecast_data.get('Predictions', {})
        
        # AWS best practice: Handle different forecast response formats
        for prediction_key, prediction_values in predictions_raw.items():
            if not isinstance(prediction_values, list):
                continue
                
            for prediction in prediction_values:
                # Validate prediction data structure
                if not isinstance(prediction, dict):
                    continue
                
                timestamp = prediction.get('Timestamp')
                value = prediction.get('Value')
                
                # AWS best practice: Skip invalid data points
                if not timestamp or value is None:
                    continue
                
                predictions.append(ForecastPrediction(
                    date=timestamp,
                    predicted_price=max(0.0, float(value)),  # Ensure non-negative prices
                    confidence_interval={
                        'lower': max(0.0, float(prediction.get('LowerBound', 0.0))),
                        'upper': max(0.0, float(prediction.get('UpperBound', 0.0)))
                    }
                ))
        
        # Analyze trend from predictions
        trend_analysis = AWSBIDataTransformer._analyze_price_trend(predictions)
        
        # AWS best practice: Provide default values for missing fields
        return ForecastResult(
            predictions=predictions,
            trend=trend_analysis.get('trend', 'stable'),
            confidence=min(1.0, max(0.0, aws_response.get('Confidence', 0.0))),
            lowest_price_date=trend_analysis.get('lowest_price_date'),
            predicted_lowest_price=trend_analysis.get('lowest_price'),
            decline_percentage=trend_analysis.get('decline_percentage', 0.0),
            forecast_horizon_days=len(predictions),
            model_accuracy=aws_response.get('ModelAccuracy'),
            seasonality_detected=trend_analysis.get('seasonality_detected', False),
            data_quality_score=min(1.0, max(0.0, aws_response.get('DataQualityScore', 0.8)))
        )
    
    @staticmethod
    def _analyze_price_trend(predictions: List[ForecastPrediction]) -> Dict[str, Any]:
        """
        Analyze price trend from forecast predictions.
        
        Args:
            predictions: List of forecast predictions
            
        Returns:
            Dictionary with trend analysis results
        """
        if len(predictions) < 2:
            return {'trend': 'stable'}
        
        prices = [p.predicted_price for p in predictions]
        
        # Simple trend analysis
        first_price = prices[0]
        last_price = prices[-1]
        min_price = min(prices)
        min_price_idx = prices.index(min_price)
        
        # Calculate trend
        price_change = (last_price - first_price) / first_price * 100
        
        if price_change > 5:
            trend = 'increasing'
        elif price_change < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        # Find lowest price date
        lowest_price_date = None
        if min_price_idx < len(predictions):
            lowest_price_date = predictions[min_price_idx].date
        
        return {
            'trend': trend,
            'lowest_price_date': lowest_price_date,
            'lowest_price': min_price,
            'decline_percentage': abs(price_change) if trend == 'declining' else 0,
            'seasonality_detected': AWSBIDataTransformer._detect_seasonality(prices)
        }
    
    @staticmethod
    def _detect_seasonality(prices: List[float]) -> bool:
        """
        Simple seasonality detection in price data.
        
        Args:
            prices: List of price values
            
        Returns:
            Boolean indicating if seasonality is detected
        """
        if len(prices) < 12:  # Need at least 12 points for seasonal analysis
            return False
        
        # Simple coefficient of variation check
        mean_price = sum(prices) / len(prices)
        variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
        cv = (variance ** 0.5) / mean_price
        
        # If coefficient of variation > 0.15, consider it seasonal
        return cv > 0.15
    
    @staticmethod
    def transform_comprehend_response(
        aws_response: Dict[str, Any], 
        product_name: str
    ) -> SentimentAnalysis:
        """
        Transform AWS Comprehend API response to SentimentAnalysis model.
        
        Following AWS best practices for Comprehend response handling.
        
        Args:
            aws_response: Raw AWS Comprehend API response
            product_name: Product name for context
            
        Returns:
            SentimentAnalysis object
            
        Raises:
            ValueError: If response format is invalid
        """
        if not aws_response:
            raise ValueError("Empty AWS Comprehend response")
        
        # AWS best practice: Handle different Comprehend response formats
        sentiment_result = aws_response.get('SentimentResult', {})
        if not sentiment_result:
            # Handle batch job responses
            sentiment_result = aws_response.get('Sentiment', {})
        
        # Extract key factors from entities and key phrases
        key_factors = []
        entities = aws_response.get('Entities', [])
        
        # AWS best practice: Validate entity data before processing
        if isinstance(entities, list):
            for entity in entities[:5]:  # Limit to top 5 entities
                if not isinstance(entity, dict):
                    continue
                
                entity_text = entity.get('Text', '').strip()
                entity_score = entity.get('Score', 0.5)
                
                # Skip empty or low-confidence entities
                if not entity_text or entity_score < 0.1:
                    continue
                
                key_factors.append(SentimentFactor(
                    factor=entity_text,
                    sentiment=sentiment_result.get('Sentiment', 'NEUTRAL'),
                    confidence=min(1.0, max(0.0, entity_score)),
                    impact_description=f"Market factor: {entity.get('Type', 'Unknown')}"
                ))
        
        # Calculate supply risk score based on sentiment
        sentiment_scores = sentiment_result.get('SentimentScore', {})
        supply_risk_score = AWSBIDataTransformer._calculate_supply_risk(
            sentiment_result.get('Sentiment', 'NEUTRAL'),
            sentiment_scores
        )
        
        # AWS best practice: Validate sentiment values
        overall_sentiment = sentiment_result.get('Sentiment', 'NEUTRAL')
        if overall_sentiment not in ['POSITIVE', 'NEGATIVE', 'NEUTRAL', 'MIXED']:
            overall_sentiment = 'NEUTRAL'
        
        # Get confidence score with fallback logic
        confidence_score = (
            sentiment_scores.get('Mixed', 0.0) or
            sentiment_scores.get('Neutral', 0.0) or
            max(sentiment_scores.values()) if sentiment_scores else 0.5
        )
        
        return SentimentAnalysis(
            overall_sentiment=overall_sentiment,
            sentiment_score=min(1.0, max(0.0, confidence_score)),
            supply_risk_score=supply_risk_score,
            demand_outlook=AWSBIDataTransformer._determine_demand_outlook(sentiment_result),
            risk_level=AWSBIDataTransformer._determine_risk_level(supply_risk_score),
            key_factors=key_factors,
            confidence_score=min(1.0, max(0.0, confidence_score)),
            news_sources_analyzed=len(aws_response.get('SourceDocuments', [])),
            analysis_date=datetime.now()
        )
    
    @staticmethod
    def _calculate_supply_risk(sentiment: str, sentiment_scores: Dict[str, float]) -> float:
        """
        Calculate supply risk score from sentiment analysis.
        
        Args:
            sentiment: Overall sentiment (POSITIVE, NEGATIVE, NEUTRAL)
            sentiment_scores: Detailed sentiment scores
            
        Returns:
            Supply risk score (0.0 to 1.0)
        """
        if sentiment == 'NEGATIVE':
            return min(0.8, sentiment_scores.get('Negative', 0.5) + 0.3)
        elif sentiment == 'POSITIVE':
            return max(0.2, 0.5 - sentiment_scores.get('Positive', 0.5) * 0.3)
        else:
            return 0.5  # Neutral risk
    
    @staticmethod
    def _determine_demand_outlook(sentiment_result: Dict[str, Any]) -> str:
        """
        Determine demand outlook from sentiment analysis.
        
        Args:
            sentiment_result: Sentiment analysis result
            
        Returns:
            Demand outlook string
        """
        sentiment = sentiment_result.get('Sentiment', 'NEUTRAL')
        scores = sentiment_result.get('SentimentScore', {})
        
        if sentiment == 'POSITIVE' and scores.get('Positive', 0) > 0.7:
            return 'Strong'
        elif sentiment == 'NEGATIVE' and scores.get('Negative', 0) > 0.7:
            return 'Weak'
        else:
            return 'Moderate'
    
    @staticmethod
    def _determine_risk_level(supply_risk_score: float) -> str:
        """
        Determine risk level from supply risk score.
        
        Args:
            supply_risk_score: Supply risk score (0.0 to 1.0)
            
        Returns:
            Risk level string
        """
        if supply_risk_score > 0.7:
            return 'HIGH'
        elif supply_risk_score > 0.4:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    @staticmethod
    def calculate_aws_bi_confidence(
        forecast_result: Optional[ForecastResult],
        sentiment_analysis: Optional[SentimentAnalysis],
        quicksight_insights: Optional[QuickSightInsights],
        data_completeness: float
    ) -> Tuple[AWSBIConfidenceFactors, float]:
        """
        Calculate overall confidence score based on AWS BI results.
        
        Args:
            forecast_result: Amazon Forecast results
            sentiment_analysis: AWS Comprehend results
            quicksight_insights: QuickSight insights
            data_completeness: Data completeness score (0.0 to 1.0)
            
        Returns:
            Tuple of (confidence factors, overall confidence score)
        """
        # Individual service confidence scores
        forecast_confidence = forecast_result.confidence if forecast_result else 0.0
        sentiment_confidence = sentiment_analysis.confidence_score if sentiment_analysis else 0.0
        quicksight_confidence = (
            quicksight_insights.data_freshness_score if quicksight_insights else 0.0
        )
        
        # Calculate source reliability based on available services
        services_available = sum([
            1 if forecast_result else 0,
            1 if sentiment_analysis else 0,
            1 if quicksight_insights else 0
        ])
        source_reliability = min(1.0, services_available / 3.0 + 0.3)
        
        # Calculate temporal relevance (assume recent data is more relevant)
        temporal_relevance = 0.9  # Default high relevance for real-time analysis
        
        confidence_factors = AWSBIConfidenceFactors(
            forecast_confidence=forecast_confidence,
            sentiment_confidence=sentiment_confidence,
            quicksight_insights_confidence=quicksight_confidence,
            data_completeness=data_completeness,
            source_reliability=source_reliability,
            temporal_relevance=temporal_relevance
        )
        
        # Weighted overall confidence calculation
        weights = {
            'forecast': 0.3,
            'sentiment': 0.2,
            'quicksight': 0.2,
            'completeness': 0.15,
            'reliability': 0.1,
            'temporal': 0.05
        }
        
        overall_confidence = (
            forecast_confidence * weights['forecast'] +
            sentiment_confidence * weights['sentiment'] +
            quicksight_confidence * weights['quicksight'] +
            data_completeness * weights['completeness'] +
            source_reliability * weights['reliability'] +
            temporal_relevance * weights['temporal']
        )
        
        return confidence_factors, min(1.0, overall_confidence)
    
    @staticmethod
    def create_quicksight_data_input(
        product_name: str,
        price_quotes: List[PriceQuote],
        market_factors: Optional[Dict[str, Any]] = None
    ) -> QuickSightDataInput:
        """
        Create QuickSight data input from price quotes and market factors.
        
        Args:
            product_name: Product name
            price_quotes: Historical price quotes
            market_factors: Additional market factor data
            
        Returns:
            QuickSightDataInput object
        """
        # Convert price quotes to time series format
        price_history = []
        for quote in price_quotes:
            if quote.cached_at:
                price_history.append({
                    'timestamp': quote.cached_at.isoformat(),
                    'price': quote.base_price,
                    'supplier': quote.supplier,
                    'location': quote.location
                })
        
        return QuickSightDataInput(
            product_name=product_name,
            price_history=price_history,
            market_factors=market_factors or {},
            location_data=None,  # Can be enhanced with location-specific data
            seasonal_indicators=None  # Can be enhanced with seasonal data
        )