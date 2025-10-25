import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from contextlib import contextmanager

from .models import (
    PriceAnalysis, ProductAnalysisResult, AnalyzeResponse,
    SupplierRecommendation, OptimizationRecommendation,
    PriceAlert, PurchaseRecord
)

logger = logging.getLogger(__name__)

class StorageError(Exception):
    """Custom exception for storage operations"""
    pass

class MarketDataCache:
    """
    Handles caching of market data including price quotes and analysis results.
    Uses JSON files for simple storage with error handling and data validation.
    """
    
    def __init__(self, cache_dir: str = "data"):
        self.cache_dir = Path(cache_dir)
        self.market_data_file = self.cache_dir / "market_data_cache.json"
        self.analysis_results_file = self.cache_dir / "analysis_results.json"
        self.price_alerts_file = self.cache_dir / "price_alerts.json"
        self.purchase_records_file = self.cache_dir / "purchase_records.json"
        
        # Ensure cache directory exists
        self._ensure_cache_directory()
        
        # Initialize cache files if they don't exist
        self._initialize_cache_files()
    
    def _ensure_cache_directory(self) -> None:
        """Create cache directory if it doesn't exist"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cache directory ensured at: {self.cache_dir}")
        except OSError as e:
            raise StorageError(f"Failed to create cache directory {self.cache_dir}: {e}")
    
    def _initialize_cache_files(self) -> None:
        """Initialize cache files with empty structures if they don't exist"""
        try:
            if not self.market_data_file.exists():
                self._write_json_file(self.market_data_file, {})
                logger.info(f"Initialized market data cache file: {self.market_data_file}")
            
            if not self.analysis_results_file.exists():
                self._write_json_file(self.analysis_results_file, {})
                logger.info(f"Initialized analysis results file: {self.analysis_results_file}")
            
            if not self.price_alerts_file.exists():
                self._write_json_file(self.price_alerts_file, {})
                logger.info(f"Initialized price alerts file: {self.price_alerts_file}")
            
            if not self.purchase_records_file.exists():
                self._write_json_file(self.purchase_records_file, {})
                logger.info(f"Initialized purchase records file: {self.purchase_records_file}")
        except Exception as e:
            raise StorageError(f"Failed to initialize cache files: {e}")
    
    @contextmanager
    def _file_lock(self, file_path: Path):
        """Simple file locking mechanism for concurrent access protection"""
        lock_file = file_path.with_suffix(file_path.suffix + '.lock')
        try:
            # Create lock file
            lock_file.touch()
            yield
        finally:
            # Remove lock file
            if lock_file.exists():
                lock_file.unlink()
    
    def _read_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Safely read JSON file with error handling"""
        try:
            with self._file_lock(file_path):
                if not file_path.exists():
                    return {}
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        return {}
                    return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            # Backup corrupted file and return empty dict
            backup_path = file_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            file_path.rename(backup_path)
            logger.info(f"Corrupted file backed up to: {backup_path}")
            return {}
        except Exception as e:
            raise StorageError(f"Failed to read {file_path}: {e}")
    
    def _write_json_file(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Safely write JSON file with error handling"""
        try:
            with self._file_lock(file_path):
                # Write to temporary file first, then rename for atomic operation
                temp_file = file_path.with_suffix('.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
                # Atomic rename
                temp_file.replace(file_path)
                logger.debug(f"Successfully wrote data to {file_path}")
        except Exception as e:
            # Clean up temp file if it exists
            temp_file = file_path.with_suffix('.tmp')
            if temp_file.exists():
                temp_file.unlink()
            raise StorageError(f"Failed to write {file_path}: {e}")
    
    def _generate_product_hash(self, product_name: str, location: str) -> str:
        """Generate a consistent hash for product + location combination"""
        import hashlib
        key = f"{product_name.lower().strip()}_{location.lower().strip()}"
        return hashlib.md5(key.encode()).hexdigest()
    
    # Market Data Caching Methods
    
    def cache_market_data(self, product_name: str, location: str, 
                         price_quotes: List[Dict[str, Any]], 
                         forecast_data: Optional[Dict[str, Any]] = None,
                         sentiment_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Cache market data for a specific product and location.
        
        Args:
            product_name: Name of the agricultural product
            location: Farm location string
            price_quotes: List of price quote dictionaries
            forecast_data: Optional forecast analysis data
            sentiment_data: Optional market sentiment data
        """
        try:
            product_hash = self._generate_product_hash(product_name, location)
            cache_data = self._read_json_file(self.market_data_file)
            
            cache_entry = {
                "product_name": product_name,
                "location": location,
                "price_quotes": price_quotes,
                "forecast_data": forecast_data,
                "sentiment_data": sentiment_data,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            cache_data[product_hash] = cache_entry
            self._write_json_file(self.market_data_file, cache_data)
            
            logger.info(f"Cached market data for {product_name} at {location}")
        except Exception as e:
            raise StorageError(f"Failed to cache market data for {product_name}: {e}")
    
    def get_cached_market_data(self, product_name: str, location: str, 
                              max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached market data if it exists and is not expired.
        
        Args:
            product_name: Name of the agricultural product
            location: Farm location string
            max_age_hours: Maximum age of cached data in hours
            
        Returns:
            Cached data dictionary or None if not found/expired
        """
        try:
            product_hash = self._generate_product_hash(product_name, location)
            cache_data = self._read_json_file(self.market_data_file)
            
            if product_hash not in cache_data:
                return None
            
            entry = cache_data[product_hash]
            last_updated = datetime.fromisoformat(entry["last_updated"])
            age_hours = (datetime.now(timezone.utc) - last_updated).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                logger.info(f"Cached data for {product_name} is expired ({age_hours:.1f}h old)")
                return None
            
            logger.info(f"Retrieved cached market data for {product_name} at {location}")
            return entry
        except Exception as e:
            logger.error(f"Failed to retrieve cached market data for {product_name}: {e}")
            return None
    
    def clear_expired_market_data(self, max_age_hours: int = 168) -> int:
        """
        Remove expired market data entries.
        
        Args:
            max_age_hours: Maximum age to keep (default: 1 week)
            
        Returns:
            Number of entries removed
        """
        try:
            cache_data = self._read_json_file(self.market_data_file)
            current_time = datetime.now(timezone.utc)
            removed_count = 0
            
            keys_to_remove = []
            for key, entry in cache_data.items():
                try:
                    last_updated = datetime.fromisoformat(entry["last_updated"])
                    age_hours = (current_time - last_updated).total_seconds() / 3600
                    
                    if age_hours > max_age_hours:
                        keys_to_remove.append(key)
                except (KeyError, ValueError):
                    # Remove entries with invalid timestamps
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del cache_data[key]
                removed_count += 1
            
            if removed_count > 0:
                self._write_json_file(self.market_data_file, cache_data)
                logger.info(f"Removed {removed_count} expired market data entries")
            
            return removed_count
        except Exception as e:
            raise StorageError(f"Failed to clear expired market data: {e}")
    
    # Advanced Optimization Features Storage Methods
    
    def save_price_alert(self, alert: PriceAlert) -> None:
        """
        Save a price alert to storage.
        
        Args:
            alert: PriceAlert object to save
        """
        try:
            alerts_data = self._read_json_file(self.price_alerts_file)
            
            # Convert Pydantic model to dict for JSON serialization
            alert_dict = alert.model_dump()
            alerts_data[alert.alert_id] = alert_dict
            
            self._write_json_file(self.price_alerts_file, alerts_data)
            logger.info(f"Saved price alert: {alert.alert_id}")
        except Exception as e:
            raise StorageError(f"Failed to save price alert {alert.alert_id}: {e}")
    
    def list_price_alerts(self, status: Optional[str] = None, 
                         product_name: Optional[str] = None,
                         limit: int = 20) -> List[Dict[str, Any]]:
        """
        List price alerts with optional filtering.
        
        Args:
            status: Filter by alert status (active, triggered, expired, cancelled)
            product_name: Filter by product name
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries
        """
        try:
            alerts_data = self._read_json_file(self.price_alerts_file)
            
            alerts = []
            for alert_id, alert_dict in alerts_data.items():
                # Apply filters
                if status and alert_dict.get("status") != status:
                    continue
                if product_name and alert_dict.get("product_name") != product_name:
                    continue
                
                alerts.append(alert_dict)
            
            # Sort by creation date (newest first)
            alerts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return alerts[:limit]
        except Exception as e:
            logger.error(f"Failed to list price alerts: {e}")
            return []
    
    def cancel_price_alert(self, alert_id: str) -> bool:
        """
        Cancel a price alert by setting its status to cancelled.
        
        Args:
            alert_id: ID of the alert to cancel
            
        Returns:
            True if alert was cancelled, False if not found
        """
        try:
            alerts_data = self._read_json_file(self.price_alerts_file)
            
            if alert_id not in alerts_data:
                return False
            
            alerts_data[alert_id]["status"] = "cancelled"
            alerts_data[alert_id]["cancelled_at"] = datetime.now(timezone.utc).isoformat()
            
            self._write_json_file(self.price_alerts_file, alerts_data)
            logger.info(f"Cancelled price alert: {alert_id}")
            return True
        except Exception as e:
            raise StorageError(f"Failed to cancel price alert {alert_id}: {e}")
    
    def save_purchase_record(self, purchase: PurchaseRecord) -> None:
        """
        Save a purchase record to storage.
        
        Args:
            purchase: PurchaseRecord object to save
        """
        try:
            records_data = self._read_json_file(self.purchase_records_file)
            
            # Convert Pydantic model to dict for JSON serialization
            purchase_dict = purchase.model_dump()
            records_data[purchase.purchase_id] = purchase_dict
            
            self._write_json_file(self.purchase_records_file, records_data)
            logger.info(f"Saved purchase record: {purchase.purchase_id}")
        except Exception as e:
            raise StorageError(f"Failed to save purchase record {purchase.purchase_id}: {e}")
    
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
            records_data = self._read_json_file(self.purchase_records_file)
            
            history = []
            for purchase_id, purchase_dict in records_data.items():
                # Filter by product name
                if purchase_dict.get("product_name") != product_name:
                    continue
                
                # Filter by supplier if specified
                if supplier and purchase_dict.get("supplier") != supplier:
                    continue
                
                history.append(purchase_dict)
            
            # Sort by purchase date (newest first)
            history.sort(key=lambda x: x.get("purchase_date", ""), reverse=True)
            
            return history[:limit]
        except Exception as e:
            logger.error(f"Failed to get purchase history for {product_name}: {e}")
            return []


class SessionStorage:
    """
    Handles session-based storage for analysis results with individual product budgets.
    Each analysis session gets a unique ID and stores complete results.
    """
    
    def __init__(self, cache_dir: str = "data"):
        self.cache_dir = Path(cache_dir)
        self.analysis_results_file = self.cache_dir / "analysis_results.json"
        
        # Ensure cache directory exists
        self._ensure_cache_directory()
        
        # Initialize analysis results file if it doesn't exist
        self._initialize_analysis_file()
    
    def _ensure_cache_directory(self) -> None:
        """Create cache directory if it doesn't exist"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise StorageError(f"Failed to create cache directory {self.cache_dir}: {e}")
    
    def _initialize_analysis_file(self) -> None:
        """Initialize analysis results file if it doesn't exist"""
        try:
            if not self.analysis_results_file.exists():
                self._write_json_file(self.analysis_results_file, {})
        except Exception as e:
            raise StorageError(f"Failed to initialize analysis results file: {e}")
    
    @contextmanager
    def _file_lock(self, file_path: Path):
        """Simple file locking mechanism for concurrent access protection"""
        lock_file = file_path.with_suffix(file_path.suffix + '.lock')
        try:
            lock_file.touch()
            yield
        finally:
            if lock_file.exists():
                lock_file.unlink()
    
    def _read_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Safely read JSON file with error handling"""
        try:
            with self._file_lock(file_path):
                if not file_path.exists():
                    return {}
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        return {}
                    return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            backup_path = file_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            file_path.rename(backup_path)
            return {}
        except Exception as e:
            raise StorageError(f"Failed to read {file_path}: {e}")
    
    def _write_json_file(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Safely write JSON file with error handling"""
        try:
            with self._file_lock(file_path):
                temp_file = file_path.with_suffix('.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                temp_file.replace(file_path)
        except Exception as e:
            temp_file = file_path.with_suffix('.tmp')
            if temp_file.exists():
                temp_file.unlink()
            raise StorageError(f"Failed to write {file_path}: {e}")
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return str(uuid.uuid4())
    
    def save_analysis_session(self, session_id: str, analysis_response: AnalyzeResponse) -> None:
        """
        Save complete analysis results for a session.
        
        Args:
            session_id: Unique session identifier
            analysis_response: Complete analysis response to store
        """
        try:
            analysis_data = self._read_json_file(self.analysis_results_file)
            
            # Convert Pydantic model to dict for JSON serialization
            session_data = {
                "session_id": session_id,
                "analysis_response": analysis_response.dict(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_accessed": datetime.now(timezone.utc).isoformat()
            }
            
            analysis_data[session_id] = session_data
            self._write_json_file(self.analysis_results_file, analysis_data)
            
            logger.info(f"Saved analysis session: {session_id}")
        except Exception as e:
            raise StorageError(f"Failed to save analysis session {session_id}: {e}")
    
    def get_analysis_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve analysis results for a specific session.
        
        Args:
            session_id: Session identifier to retrieve
            
        Returns:
            Session data dictionary or None if not found
        """
        try:
            analysis_data = self._read_json_file(self.analysis_results_file)
            
            if session_id not in analysis_data:
                return None
            
            session_data = analysis_data[session_id]
            
            # Update last accessed timestamp
            session_data["last_accessed"] = datetime.now(timezone.utc).isoformat()
            analysis_data[session_id] = session_data
            self._write_json_file(self.analysis_results_file, analysis_data)
            
            logger.info(f"Retrieved analysis session: {session_id}")
            return session_data
        except Exception as e:
            logger.error(f"Failed to retrieve analysis session {session_id}: {e}")
            return None
    
    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List recent analysis sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session summaries sorted by creation date (newest first)
        """
        try:
            analysis_data = self._read_json_file(self.analysis_results_file)
            
            sessions = []
            for session_id, session_data in analysis_data.items():
                summary = {
                    "session_id": session_id,
                    "created_at": session_data.get("created_at"),
                    "last_accessed": session_data.get("last_accessed"),
                    "product_count": len(session_data.get("analysis_response", {}).get("product_analyses", [])),
                    "total_budget": session_data.get("analysis_response", {}).get("overall_budget", {}).get("target", 0)
                }
                sessions.append(summary)
            
            # Sort by creation date (newest first)
            sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return sessions[:limit]
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a specific analysis session.
        
        Args:
            session_id: Session identifier to delete
            
        Returns:
            True if session was deleted, False if not found
        """
        try:
            analysis_data = self._read_json_file(self.analysis_results_file)
            
            if session_id not in analysis_data:
                return False
            
            del analysis_data[session_id]
            self._write_json_file(self.analysis_results_file, analysis_data)
            
            logger.info(f"Deleted analysis session: {session_id}")
            return True
        except Exception as e:
            raise StorageError(f"Failed to delete analysis session {session_id}: {e}")
    
    def cleanup_old_sessions(self, max_age_days: int = 30) -> int:
        """
        Remove old analysis sessions.
        
        Args:
            max_age_days: Maximum age to keep sessions (default: 30 days)
            
        Returns:
            Number of sessions removed
        """
        try:
            analysis_data = self._read_json_file(self.analysis_results_file)
            current_time = datetime.now(timezone.utc)
            removed_count = 0
            
            sessions_to_remove = []
            for session_id, session_data in analysis_data.items():
                try:
                    created_at = datetime.fromisoformat(session_data["created_at"])
                    age_seconds = (current_time - created_at).total_seconds()
                    age_days = age_seconds / (24 * 3600)  # Convert to days with fractional precision
                    
                    if age_days > max_age_days:
                        sessions_to_remove.append(session_id)
                except (KeyError, ValueError):
                    # Remove sessions with invalid timestamps
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del analysis_data[session_id]
                removed_count += 1
            
            if removed_count > 0:
                self._write_json_file(self.analysis_results_file, analysis_data)
                logger.info(f"Removed {removed_count} old analysis sessions")
            
            return removed_count
        except Exception as e:
            raise StorageError(f"Failed to cleanup old sessions: {e}")


# Convenience functions for easy access
def get_market_cache() -> MarketDataCache:
    """Get a MarketDataCache instance"""
    return MarketDataCache()

def get_session_storage() -> SessionStorage:
    """Get a SessionStorage instance"""
    return SessionStorage()