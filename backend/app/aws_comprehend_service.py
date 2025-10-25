import boto3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from botocore.exceptions import ClientError, BotoCoreError
import re

logger = logging.getLogger(__name__)

class AWSComprehendService:
    """
    Service for integrating with AWS Comprehend to analyze market sentiment and generate risk assessments.
    Handles market news analysis, supply risk scoring, and demand outlook predictions.
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        """Initialize the AWS Comprehend service client."""
        try:
            self.comprehend_client = boto3.client('comprehend', region_name=region_name)
            self.region = region_name
        except Exception as e:
            logger.error(f"Failed to initialize AWS Comprehend client: {str(e)}")
            raise
    
    def analyze_market_news_sentiment(self, news_articles: List[Dict]) -> Dict:
        """
        Analyze sentiment of market news and reports related to agricultural products.
        
        Args:
            news_articles: List of news articles with 'title', 'content', and 'product' fields
            
        Returns:
            Dict containing sentiment analysis results
        """
        try:
            if not news_articles:
                return {
                    'analysis_completed': False,
                    'reason': 'No news articles provided for analysis'
                }
            
            sentiment_results = []
            
            for article in news_articles:
                title = article.get('title', '')
                content = article.get('content', '')
                product = article.get('product', 'unknown')
                
                # Combine title and content for analysis
                full_text = f"{title}. {content}".strip()
                
                if len(full_text) < 10:  # Skip very short texts
                    continue
                
                # Truncate text if too long (Comprehend has limits)
                if len(full_text) > 5000:
                    full_text = full_text[:5000]
                
                try:
                    # Analyze sentiment using AWS Comprehend
                    sentiment_response = self.comprehend_client.detect_sentiment(
                        Text=full_text,
                        LanguageCode='en'
                    )
                    
                    # Extract key phrases for additional context
                    phrases_response = self.comprehend_client.detect_key_phrases(
                        Text=full_text,
                        LanguageCode='en'
                    )
                    
                    # Extract entities (organizations, locations, etc.)
                    entities_response = self.comprehend_client.detect_entities(
                        Text=full_text,
                        LanguageCode='en'
                    )
                    
                    sentiment_results.append({
                        'product': product,
                        'title': title,
                        'sentiment': sentiment_response['Sentiment'],
                        'sentiment_scores': {
                            'positive': float(sentiment_response['SentimentScore']['Positive']),
                            'negative': float(sentiment_response['SentimentScore']['Negative']),
                            'neutral': float(sentiment_response['SentimentScore']['Neutral']),
                            'mixed': float(sentiment_response['SentimentScore']['Mixed'])
                        },
                        'key_phrases': [
                            {
                                'text': phrase['Text'],
                                'confidence': float(phrase['Score'])
                            }
                            for phrase in phrases_response['KeyPhrases'][:10]  # Top 10 phrases
                        ],
                        'entities': [
                            {
                                'text': entity['Text'],
                                'type': entity['Type'],
                                'confidence': float(entity['Score'])
                            }
                            for entity in entities_response['Entities'][:10]  # Top 10 entities
                        ]
                    })
                    
                except ClientError as e:
                    logger.warning(f"Failed to analyze article sentiment: {str(e)}")
                    continue
            
            # Aggregate sentiment by product
            product_sentiment = self._aggregate_sentiment_by_product(sentiment_results)
            
            return {
                'analysis_completed': True,
                'articles_analyzed': len(sentiment_results),
                'individual_results': sentiment_results,
                'product_sentiment_summary': product_sentiment
            }
            
        except Exception as e:
            logger.error(f"Market news sentiment analysis failed: {str(e)}")
            return {
                'analysis_completed': False,
                'error': str(e)
            }
    
    def calculate_supply_risk_score(self, sentiment_data: Dict, 
                                  market_factors: Dict) -> Dict:
        """
        Calculate supply risk scoring based on sentiment analysis and market factors.
        
        Args:
            sentiment_data: Results from sentiment analysis
            market_factors: Additional market factors (weather, geopolitical, etc.)
            
        Returns:
            Dict containing supply risk scores and analysis
        """
        try:
            risk_scores = {}
            
            # Process sentiment data for each product
            product_sentiments = sentiment_data.get('product_sentiment_summary', {})
            
            for product, sentiment_info in product_sentiments.items():
                base_risk_score = 0.5  # Neutral baseline (0-1 scale)
                
                # Adjust based on sentiment
                avg_sentiment = sentiment_info.get('average_sentiment_score', 0.5)
                negative_ratio = sentiment_info.get('negative_ratio', 0.0)
                
                # Higher negative sentiment increases risk
                sentiment_risk = negative_ratio * 0.4  # Max 40% from sentiment
                
                # Adjust based on market factors
                weather_risk = market_factors.get('weather_risk', 0.0)  # 0-1 scale
                geopolitical_risk = market_factors.get('geopolitical_risk', 0.0)
                supply_chain_risk = market_factors.get('supply_chain_risk', 0.0)
                
                # Calculate composite risk score
                total_risk = min(1.0, base_risk_score + sentiment_risk + 
                               (weather_risk * 0.3) + (geopolitical_risk * 0.2) + 
                               (supply_chain_risk * 0.1))
                
                # Classify risk level
                if total_risk >= 0.8:
                    risk_level = 'very_high'
                elif total_risk >= 0.6:
                    risk_level = 'high'
                elif total_risk >= 0.4:
                    risk_level = 'medium'
                elif total_risk >= 0.2:
                    risk_level = 'low'
                else:
                    risk_level = 'very_low'
                
                # Generate risk factors explanation
                risk_factors = []
                if negative_ratio > 0.3:
                    risk_factors.append(f"High negative sentiment in market news ({negative_ratio:.1%})")
                if weather_risk > 0.5:
                    risk_factors.append("Adverse weather conditions reported")
                if geopolitical_risk > 0.5:
                    risk_factors.append("Geopolitical tensions affecting supply")
                if supply_chain_risk > 0.5:
                    risk_factors.append("Supply chain disruptions identified")
                
                risk_scores[product] = {
                    'risk_score': float(total_risk),
                    'risk_level': risk_level,
                    'contributing_factors': {
                        'sentiment_risk': float(sentiment_risk),
                        'weather_risk': float(weather_risk),
                        'geopolitical_risk': float(geopolitical_risk),
                        'supply_chain_risk': float(supply_chain_risk)
                    },
                    'risk_factors': risk_factors,
                    'confidence': sentiment_info.get('confidence', 0.5)
                }
            
            return {
                'risk_calculation_completed': True,
                'products_analyzed': len(risk_scores),
                'risk_scores': risk_scores,
                'overall_market_risk': self._calculate_overall_market_risk(risk_scores)
            }
            
        except Exception as e:
            logger.error(f"Supply risk calculation failed: {str(e)}")
            return {
                'risk_calculation_completed': False,
                'error': str(e)
            }
    
    def predict_demand_outlook(self, sentiment_data: Dict, 
                             historical_demand: List[Dict]) -> Dict:
        """
        Generate demand outlook predictions based on sentiment analysis.
        
        Args:
            sentiment_data: Results from sentiment analysis
            historical_demand: Historical demand data
            
        Returns:
            Dict containing demand outlook predictions
        """
        try:
            demand_predictions = {}
            
            product_sentiments = sentiment_data.get('product_sentiment_summary', {})
            
            for product, sentiment_info in product_sentiments.items():
                # Find historical demand for this product
                product_demand = [
                    d for d in historical_demand 
                    if d.get('product', '').lower() == product.lower()
                ]
                
                if not product_demand:
                    continue
                
                # Calculate baseline demand trend
                recent_demand = product_demand[-30:] if len(product_demand) >= 30 else product_demand
                avg_demand = sum(d.get('quantity', 0) for d in recent_demand) / len(recent_demand)
                
                # Adjust based on sentiment
                positive_ratio = sentiment_info.get('positive_ratio', 0.0)
                negative_ratio = sentiment_info.get('negative_ratio', 0.0)
                
                # Positive sentiment generally increases demand, negative decreases it
                sentiment_multiplier = 1.0 + (positive_ratio * 0.2) - (negative_ratio * 0.15)
                
                # Predict demand for next 30 days
                predicted_demand = avg_demand * sentiment_multiplier
                
                # Calculate confidence based on sentiment consistency and data quality
                sentiment_consistency = 1.0 - sentiment_info.get('mixed_ratio', 0.0)
                data_quality = min(1.0, len(product_demand) / 90)  # 90 days ideal
                confidence = (sentiment_consistency + data_quality) / 2
                
                # Determine outlook category
                change_percent = (predicted_demand - avg_demand) / avg_demand * 100
                
                if change_percent >= 10:
                    outlook = 'increasing'
                elif change_percent <= -10:
                    outlook = 'decreasing'
                else:
                    outlook = 'stable'
                
                demand_predictions[product] = {
                    'predicted_demand': float(predicted_demand),
                    'baseline_demand': float(avg_demand),
                    'change_percent': float(change_percent),
                    'outlook': outlook,
                    'confidence': float(confidence),
                    'sentiment_influence': {
                        'positive_impact': float(positive_ratio * 0.2),
                        'negative_impact': float(negative_ratio * 0.15),
                        'net_sentiment_effect': float(sentiment_multiplier - 1.0)
                    }
                }
            
            return {
                'prediction_completed': True,
                'products_analyzed': len(demand_predictions),
                'demand_predictions': demand_predictions,
                'prediction_horizon_days': 30
            }
            
        except Exception as e:
            logger.error(f"Demand outlook prediction failed: {str(e)}")
            return {
                'prediction_completed': False,
                'error': str(e)
            }
    
    def generate_risk_based_recommendations(self, risk_scores: Dict, 
                                          demand_predictions: Dict,
                                          current_prices: Dict) -> Dict:
        """
        Generate risk-based recommendations for agricultural product purchasing.
        
        Args:
            risk_scores: Supply risk scores by product
            demand_predictions: Demand outlook predictions
            current_prices: Current market prices
            
        Returns:
            Dict containing risk-based recommendations
        """
        try:
            recommendations = []
            
            # Analyze each product
            all_products = set(risk_scores.keys()) | set(demand_predictions.keys()) | set(current_prices.keys())
            
            for product in all_products:
                risk_info = risk_scores.get(product, {})
                demand_info = demand_predictions.get(product, {})
                current_price = current_prices.get(product, 0)
                
                risk_level = risk_info.get('risk_level', 'medium')
                demand_outlook = demand_info.get('outlook', 'stable')
                
                # Generate recommendations based on risk and demand
                product_recommendations = []
                
                # High risk recommendations
                if risk_level in ['high', 'very_high']:
                    if demand_outlook == 'increasing':
                        product_recommendations.append({
                            'type': 'URGENT_PURCHASE',
                            'priority': 'high',
                            'action': f'Consider immediate purchase of {product} due to high supply risk and increasing demand',
                            'reasoning': 'High supply risk combined with increasing demand may lead to significant price increases',
                            'time_sensitivity': 'immediate'
                        })
                    else:
                        product_recommendations.append({
                            'type': 'SUPPLY_RISK',
                            'priority': 'medium',
                            'action': f'Monitor {product} supply closely and consider alternative suppliers',
                            'reasoning': 'High supply risk detected but demand is not increasing rapidly',
                            'time_sensitivity': 'within_week'
                        })
                
                # Low risk with increasing demand
                elif risk_level in ['low', 'very_low'] and demand_outlook == 'increasing':
                    product_recommendations.append({
                        'type': 'TIMING',
                        'priority': 'medium',
                        'action': f'Consider purchasing {product} soon to avoid demand-driven price increases',
                        'reasoning': 'Low supply risk but increasing demand may drive prices up',
                        'time_sensitivity': 'within_month'
                    })
                
                # High demand with stable supply
                elif demand_outlook == 'decreasing' and risk_level in ['low', 'medium']:
                    product_recommendations.append({
                        'type': 'TIMING',
                        'priority': 'low',
                        'action': f'Delay {product} purchase if possible - prices may decrease',
                        'reasoning': 'Decreasing demand with stable supply suggests potential price reductions',
                        'time_sensitivity': 'flexible'
                    })
                
                # Anomaly detection recommendations
                risk_factors = risk_info.get('risk_factors', [])
                if any('sentiment' in factor.lower() for factor in risk_factors):
                    product_recommendations.append({
                        'type': 'ANOMALY_ALERT',
                        'priority': 'medium',
                        'action': f'Investigate market conditions for {product} - unusual sentiment patterns detected',
                        'reasoning': 'Negative sentiment in market news may indicate emerging issues',
                        'time_sensitivity': 'within_week'
                    })
                
                # Add product-specific recommendations to main list
                for rec in product_recommendations:
                    rec['product'] = product
                    rec['current_price'] = current_price
                    rec['risk_score'] = risk_info.get('risk_score', 0.5)
                    rec['demand_change'] = demand_info.get('change_percent', 0)
                    recommendations.append(rec)
            
            # Sort recommendations by priority and risk
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            recommendations.sort(
                key=lambda x: (priority_order.get(x['priority'], 0), x['risk_score']), 
                reverse=True
            )
            
            # Generate summary insights
            high_priority_count = sum(1 for r in recommendations if r['priority'] == 'high')
            urgent_actions = [r for r in recommendations if r['time_sensitivity'] == 'immediate']
            
            return {
                'recommendations_generated': True,
                'total_recommendations': len(recommendations),
                'high_priority_count': high_priority_count,
                'urgent_actions_count': len(urgent_actions),
                'recommendations': recommendations,
                'summary': {
                    'immediate_attention_required': len(urgent_actions) > 0,
                    'high_risk_products': [r['product'] for r in recommendations if r['risk_score'] > 0.7],
                    'recommended_immediate_purchases': [
                        r['product'] for r in urgent_actions if r['type'] == 'URGENT_PURCHASE'
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Risk-based recommendation generation failed: {str(e)}")
            return {
                'recommendations_generated': False,
                'error': str(e)
            }
    
    def _aggregate_sentiment_by_product(self, sentiment_results: List[Dict]) -> Dict:
        """
        Aggregate sentiment analysis results by product.
        
        Args:
            sentiment_results: List of individual sentiment analysis results
            
        Returns:
            Dict containing aggregated sentiment by product
        """
        product_aggregates = {}
        
        for result in sentiment_results:
            product = result['product']
            
            if product not in product_aggregates:
                product_aggregates[product] = {
                    'articles_count': 0,
                    'sentiment_scores': {'positive': [], 'negative': [], 'neutral': [], 'mixed': []},
                    'sentiments': []
                }
            
            agg = product_aggregates[product]
            agg['articles_count'] += 1
            agg['sentiments'].append(result['sentiment'])
            
            for sentiment_type, score in result['sentiment_scores'].items():
                agg['sentiment_scores'][sentiment_type].append(score)
        
        # Calculate aggregated metrics
        for product, agg in product_aggregates.items():
            # Average sentiment scores
            avg_scores = {}
            for sentiment_type, scores in agg['sentiment_scores'].items():
                avg_scores[sentiment_type] = sum(scores) / len(scores) if scores else 0.0
            
            # Sentiment distribution
            sentiment_counts = {}
            for sentiment in agg['sentiments']:
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            total_articles = agg['articles_count']
            sentiment_ratios = {
                sentiment: count / total_articles 
                for sentiment, count in sentiment_counts.items()
            }
            
            # Overall sentiment score (weighted average)
            overall_score = (avg_scores['positive'] * 1.0 + 
                           avg_scores['neutral'] * 0.5 + 
                           avg_scores['negative'] * 0.0 + 
                           avg_scores['mixed'] * 0.3)
            
            product_aggregates[product] = {
                'articles_analyzed': total_articles,
                'average_sentiment_scores': avg_scores,
                'sentiment_distribution': sentiment_counts,
                'sentiment_ratios': sentiment_ratios,
                'positive_ratio': sentiment_ratios.get('POSITIVE', 0.0),
                'negative_ratio': sentiment_ratios.get('NEGATIVE', 0.0),
                'neutral_ratio': sentiment_ratios.get('NEUTRAL', 0.0),
                'mixed_ratio': sentiment_ratios.get('MIXED', 0.0),
                'average_sentiment_score': overall_score,
                'confidence': min(1.0, total_articles / 10)  # Higher confidence with more articles
            }
        
        return product_aggregates
    
    def _calculate_overall_market_risk(self, risk_scores: Dict) -> Dict:
        """
        Calculate overall market risk from individual product risk scores.
        
        Args:
            risk_scores: Risk scores by product
            
        Returns:
            Dict containing overall market risk assessment
        """
        if not risk_scores:
            return {'overall_risk_level': 'unknown', 'risk_score': 0.5}
        
        # Calculate weighted average risk
        total_risk = sum(info['risk_score'] for info in risk_scores.values())
        avg_risk = total_risk / len(risk_scores)
        
        # Count products by risk level
        risk_level_counts = {}
        for info in risk_scores.values():
            level = info['risk_level']
            risk_level_counts[level] = risk_level_counts.get(level, 0) + 1
        
        # Determine overall risk level
        high_risk_products = risk_level_counts.get('high', 0) + risk_level_counts.get('very_high', 0)
        total_products = len(risk_scores)
        
        if high_risk_products / total_products >= 0.5:
            overall_level = 'high'
        elif avg_risk >= 0.6:
            overall_level = 'medium_high'
        elif avg_risk >= 0.4:
            overall_level = 'medium'
        else:
            overall_level = 'low'
        
        return {
            'overall_risk_level': overall_level,
            'risk_score': float(avg_risk),
            'high_risk_product_count': high_risk_products,
            'total_products': total_products,
            'risk_distribution': risk_level_counts
        }