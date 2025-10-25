"""
Utility functions for integrating the storage system with the application.
Provides convenient methods for common storage operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging

from .storage import MarketDataCache, SessionStorage, get_market_cache, get_session_storage
from .models import (
    ProductInput, FarmLocation, AnalyzeResponse, 
    SupplierRecommendation, OptimizationRecommendation,
    PriceAlert, PurchaseRecord
)

logger = logging.getLogger(__name__)

class StorageManager:
    """
    High-level storage manager that provides convenient methods for 
    common storage operations in the farmer budget optimizer.
    """
    
    def __init__(self):
        self.market_cache = get_market_cache()
        self.session_storage = get_session_storage()
    
    # Market Data Operations
    
    def cache_product_prices(self, product_name: str, farm_location: FarmLocation, 
                           suppliers: List[SupplierRecommendation],
                           forecast_data: Optional[Dict[str, Any]] = None,
                           sentiment_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Cache price data for a product from supplier recommendations.
        
        Args:
            product_name: Name of the agricultural product
            farm_location: Farm location information
            suppliers: List of supplier recommendations
            forecast_data: Optional forecast analysis data
            sentiment_data: Optional market sentiment data
        """
        try:
            location_str = f"{farm_location.city}, {farm_location.state}, {farm_location.country}"
            
            # Convert supplier recommendations to price quotes format
            price_quotes = []
            for supplier in suppliers:
                quote = {
                    "supplier": supplier.name,
                    "price": supplier.price,
                    "unit": "unit",  # Default unit, should be passed from product
                    "moq": supplier.moq,
                    "location": supplier.location,
                    "delivery_terms": supplier.delivery_terms,
                    "lead_time": supplier.lead_time,
                    "reliability_score": supplier.reliability,
                    "contact_info": supplier.contact_info,
                    "cached_at": datetime.now(timezone.utc).isoformat()
                }
                price_quotes.append(quote)
            
            self.market_cache.cache_market_data(
                product_name, location_str, price_quotes, 
                forecast_data, sentiment_data
            )
            
            logger.info(f"Cached price data for {product_name} with {len(suppliers)} suppliers")
        except Exception as e:
            logger.error(f"Failed to cache product prices for {product_name}: {e}")
    
    def get_cached_product_prices(self, product_name: str, farm_location: FarmLocation,
                                max_age_hours: int = 24) -> Optional[List[SupplierRecommendation]]:
        """
        Retrieve cached price data as supplier recommendations.
        
        Args:
            product_name: Name of the agricultural product
            farm_location: Farm location information
            max_age_hours: Maximum age of cached data in hours
            
        Returns:
            List of supplier recommendations or None if not cached/expired
        """
        try:
            location_str = f"{farm_location.city}, {farm_location.state}, {farm_location.country}"
            
            cached_data = self.market_cache.get_cached_market_data(
                product_name, location_str, max_age_hours
            )
            
            if not cached_data:
                return None
            
            # Convert price quotes back to supplier recommendations
            suppliers = []
            for quote in cached_data.get("price_quotes", []):
                supplier = SupplierRecommendation(
                    name=quote.get("supplier", "Unknown"),
                    price=quote.get("price", 0.0),
                    delivery_terms=quote.get("delivery_terms"),
                    lead_time=quote.get("lead_time"),
                    reliability=quote.get("reliability_score"),
                    moq=quote.get("moq"),
                    contact_info=quote.get("contact_info"),
                    location=quote.get("location")
                )
                suppliers.append(supplier)
            
            logger.info(f"Retrieved {len(suppliers)} cached suppliers for {product_name}")
            return suppliers
        except Exception as e:
            logger.error(f"Failed to retrieve cached prices for {product_name}: {e}")
            return None
    
    # Session Management Operations
    
    def save_analysis_result(self, analysis_response: AnalyzeResponse) -> str:
        """
        Save analysis results and return session ID.
        
        Args:
            analysis_response: Complete analysis response to store
            
        Returns:
            Session ID for the saved analysis
        """
        try:
            session_id = self.session_storage.generate_session_id()
            self.session_storage.save_analysis_session(session_id, analysis_response)
            
            logger.info(f"Saved analysis result with session ID: {session_id}")
            return session_id
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
            raise
    
    def get_analysis_result(self, session_id: str) -> Optional[AnalyzeResponse]:
        """
        Retrieve analysis results by session ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Analysis response or None if not found
        """
        try:
            session_data = self.session_storage.get_analysis_session(session_id)
            
            if not session_data:
                return None
            
            # Convert dict back to Pydantic model
            response_data = session_data["analysis_response"]
            analysis_response = AnalyzeResponse(**response_data)
            
            logger.info(f"Retrieved analysis result for session: {session_id}")
            return analysis_response
        except Exception as e:
            logger.error(f"Failed to retrieve analysis result for {session_id}: {e}")
            return None
    
    def list_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of recent analysis sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session summaries
        """
        try:
            sessions = self.session_storage.list_sessions(limit)
            logger.info(f"Retrieved {len(sessions)} recent analysis sessions")
            return sessions
        except Exception as e:
            logger.error(f"Failed to list recent analyses: {e}")
            return []
    
    # Maintenance Operations
    
    def cleanup_old_data(self, market_data_max_age_hours: int = 168,
                        session_max_age_days: int = 30) -> Dict[str, int]:
        """
        Clean up old cached data and analysis sessions.
        
        Args:
            market_data_max_age_hours: Max age for market data (default: 1 week)
            session_max_age_days: Max age for analysis sessions (default: 30 days)
            
        Returns:
            Dictionary with cleanup statistics
        """
        try:
            market_removed = self.market_cache.clear_expired_market_data(market_data_max_age_hours)
            sessions_removed = self.session_storage.cleanup_old_sessions(session_max_age_days)
            
            cleanup_stats = {
                "market_data_removed": market_removed,
                "sessions_removed": sessions_removed,
                "cleanup_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Cleanup completed: {cleanup_stats}")
            return cleanup_stats
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return {"error": str(e)}
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored data.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            # Get session count
            sessions = self.session_storage.list_sessions(limit=1000)  # Get all sessions
            session_count = len(sessions)
            
            # Calculate total budget from recent sessions
            total_budgets = []
            for session in sessions[:10]:  # Check last 10 sessions
                try:
                    session_data = self.session_storage.get_analysis_session(session["session_id"])
                    if session_data:
                        budget = session_data["analysis_response"]["overall_budget"]["target"]
                        total_budgets.append(budget)
                except:
                    continue
            
            avg_budget = sum(total_budgets) / len(total_budgets) if total_budgets else 0
            
            stats = {
                "total_sessions": session_count,
                "recent_sessions": len(sessions[:10]),
                "average_budget": avg_budget,
                "stats_generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Generated storage statistics: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Failed to generate storage statistics: {e}")
            return {"error": str(e)}
    
    # Advanced Optimization Features Operations
    
    def save_price_alert(self, alert: PriceAlert) -> None:
        """
        Save a price alert.
        
        Args:
            alert: PriceAlert object to save
        """
        try:
            self.market_cache.save_price_alert(alert)
            logger.info(f"Saved price alert: {alert.alert_id}")
        except Exception as e:
            logger.error(f"Failed to save price alert: {e}")
            raise
    
    def list_price_alerts(self, status: Optional[str] = None, 
                         product_name: Optional[str] = None,
                         limit: int = 20) -> List[Dict[str, Any]]:
        """
        List price alerts with optional filtering.
        
        Args:
            status: Filter by alert status
            product_name: Filter by product name
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries
        """
        try:
            alerts = self.market_cache.list_price_alerts(status, product_name, limit)
            logger.info(f"Retrieved {len(alerts)} price alerts")
            return alerts
        except Exception as e:
            logger.error(f"Failed to list price alerts: {e}")
            return []
    
    def cancel_price_alert(self, alert_id: str) -> bool:
        """
        Cancel a price alert.
        
        Args:
            alert_id: ID of the alert to cancel
            
        Returns:
            True if alert was cancelled, False if not found
        """
        try:
            success = self.market_cache.cancel_price_alert(alert_id)
            if success:
                logger.info(f"Cancelled price alert: {alert_id}")
            else:
                logger.warning(f"Price alert not found: {alert_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to cancel price alert: {e}")
            return False
    
    def save_purchase_record(self, purchase: PurchaseRecord) -> None:
        """
        Save a purchase record.
        
        Args:
            purchase: PurchaseRecord object to save
        """
        try:
            self.market_cache.save_purchase_record(purchase)
            logger.info(f"Saved purchase record: {purchase.purchase_id}")
        except Exception as e:
            logger.error(f"Failed to save purchase record: {e}")
            raise
    
    def get_purchase_history(self, product_name: str, 
                           limit: int = 50,
                           supplier: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get purchase history for a specific product.
        
        Args:
            product_name: Name of the product
            limit: Maximum number of records to return
            supplier: Optional supplier filter
            
        Returns:
            List of purchase record dictionaries
        """
        try:
            history = self.market_cache.get_purchase_history(product_name, limit, supplier)
            logger.info(f"Retrieved {len(history)} purchase records for {product_name}")
            return history
        except Exception as e:
            logger.error(f"Failed to get purchase history: {e}")
            return []


# Convenience function for easy access
def get_storage_manager() -> StorageManager:
    """Get a StorageManager instance"""
    return StorageManager()