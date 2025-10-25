"""
Market Data Service for Agricultural Products

This module provides real market data collection from various sources including:
- USDA APIs for commodity prices
- Web scraping for agricultural supply websites
- Data validation and cleaning
- Caching mechanism for performance
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, quote
import re
from bs4 import BeautifulSoup
import hashlib
import time

from .storage import MarketDataCache, StorageError
from .models import FarmLocation

logger = logging.getLogger(__name__)

@dataclass
class PriceQuote:
    """Represents a price quote from a market data source"""
    supplier: str
    base_price: float
    unit: str
    product_name: str
    location: str
    source: str
    moq: Optional[int] = None
    delivery_terms: Optional[str] = None
    lead_time: Optional[int] = None
    reliability_score: Optional[float] = None
    contact_info: Optional[str] = None
    specifications: Optional[str] = None
    purity_grade: Optional[str] = None
    pack_size: Optional[str] = None
    promotions: Optional[str] = None
    price_breaks: Optional[Dict[int, float]] = None
    cached_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "supplier": self.supplier,
            "base_price": self.base_price,
            "unit": self.unit,
            "product_name": self.product_name,
            "location": self.location,
            "source": self.source,
            "moq": self.moq,
            "delivery_terms": self.delivery_terms,
            "lead_time": self.lead_time,
            "reliability_score": self.reliability_score,
            "contact_info": self.contact_info,
            "specifications": self.specifications,
            "purity_grade": self.purity_grade,
            "pack_size": self.pack_size,
            "promotions": self.promotions,
            "price_breaks": self.price_breaks,
            "cached_at": self.cached_at.isoformat() if self.cached_at else None
        }

class DataSource:
    """Base class for market data sources"""
    
    def __init__(self, name: str, base_url: str, rate_limit_delay: float = 1.0):
        self.name = name
        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
    
    async def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    async def get_prices(self, product_name: str, location: FarmLocation) -> List[PriceQuote]:
        """Get price quotes for a product. Must be implemented by subclasses."""
        raise NotImplementedError

class USDADataSource(DataSource):
    """USDA NASS (National Agricultural Statistics Service) data source"""
    
    def __init__(self):
        super().__init__(
            name="USDA_NASS",
            base_url="https://quickstats.nass.usda.gov/api",
            rate_limit_delay=1.0
        )
        # USDA API key would be set via environment variable in production
        self.api_key = "YOUR_USDA_API_KEY"  # Replace with actual key
    
    def _normalize_product_name(self, product_name: str) -> str:
        """Normalize product name for USDA commodity matching"""
        # Map common agricultural inputs to USDA commodity names
        commodity_mapping = {
            "corn seed": "CORN",
            "soybean seed": "SOYBEANS", 
            "wheat seed": "WHEAT",
            "fertilizer": "FERTILIZER",
            "nitrogen": "FERTILIZER, NITROGEN",
            "phosphorus": "FERTILIZER, PHOSPHORUS",
            "potassium": "FERTILIZER, POTASH",
            "diesel fuel": "FUEL, DIESEL",
            "gasoline": "FUEL, GASOLINE"
        }
        
        normalized = product_name.lower().strip()
        return commodity_mapping.get(normalized, product_name.upper())
    
    async def get_prices(self, product_name: str, location: FarmLocation) -> List[PriceQuote]:
        """Get USDA commodity price data"""
        await self._rate_limit()
        
        try:
            commodity = self._normalize_product_name(product_name)
            
            # USDA QuickStats API parameters
            params = {
                "key": self.api_key,
                "source_desc": "SURVEY",
                "sector_desc": "CROPS",
                "commodity_desc": commodity,
                "state_alpha": location.state,
                "statisticcat_desc": "PRICE RECEIVED",
                "format": "JSON",
                "year": datetime.now().year
            }
            
            # For MVP, use mock data instead of real USDA API
            # In production, this would make actual HTTP requests
            logger.info(f"USDA API call simulated for {commodity}")
            return []  # Return empty for now, will be implemented with real API
        
        except Exception as e:
            logger.error(f"Error fetching USDA data for {product_name}: {e}")
            return []
    
    def _parse_usda_response(self, data: Dict, product_name: str, location: FarmLocation) -> List[PriceQuote]:
        """Parse USDA API response into PriceQuote objects"""
        quotes = []
        
        try:
            if "data" not in data:
                return quotes
            
            for item in data["data"]:
                try:
                    price_str = item.get("Value", "").replace(",", "")
                    if not price_str or price_str == "(D)":  # (D) means data withheld
                        continue
                    
                    base_price = float(price_str)
                    unit = item.get("unit_desc", "")
                    
                    quote = PriceQuote(
                        supplier="USDA Market Average",
                        base_price=base_price,
                        unit=unit,
                        product_name=product_name,
                        location=f"{location.state}, {location.country}",
                        source=self.name,
                        reliability_score=0.9,  # USDA data is highly reliable
                        cached_at=datetime.now(timezone.utc)
                    )
                    quotes.append(quote)
                
                except (ValueError, KeyError) as e:
                    logger.debug(f"Skipping invalid USDA data item: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing USDA response: {e}")
        
        return quotes

class AgSupplyWebScraper(DataSource):
    """Web scraper for agricultural supply websites"""
    
    def __init__(self):
        super().__init__(
            name="AgSupply_Scraper",
            base_url="",
            rate_limit_delay=2.0  # Be respectful with scraping
        )
        
        # List of agricultural supply websites to scrape
        self.target_sites = [
            {
                "name": "AgriSupply",
                "base_url": "https://www.agrisupply.com",
                "search_path": "/search",
                "selectors": {
                    "product": ".product-item",
                    "name": ".product-name",
                    "price": ".price",
                    "unit": ".unit"
                }
            },
            {
                "name": "TractorSupply", 
                "base_url": "https://www.tractorsupply.com",
                "search_path": "/search",
                "selectors": {
                    "product": ".product-tile",
                    "name": ".product-title",
                    "price": ".price-current",
                    "unit": ".price-unit"
                }
            }
        ]
    
    async def get_prices(self, product_name: str, location: FarmLocation) -> List[PriceQuote]:
        """Scrape agricultural supply websites for product prices"""
        all_quotes = []
        
        for site in self.target_sites:
            try:
                quotes = await self._scrape_site(site, product_name, location)
                all_quotes.extend(quotes)
                await self._rate_limit()  # Rate limit between sites
            except Exception as e:
                logger.error(f"Error scraping {site['name']}: {e}")
                continue
        
        return all_quotes
    
    async def _scrape_site(self, site: Dict, product_name: str, location: FarmLocation) -> List[PriceQuote]:
        """Scrape a specific agricultural supply website"""
        quotes = []
        
        try:
            search_url = f"{site['base_url']}{site['search_path']}"
            params = {"q": product_name}
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # For MVP, use mock data instead of real web scraping
            # In production, this would make actual HTTP requests
            logger.info(f"Web scraping simulated for {site['name']}")
            quotes = []  # Return empty for now, will be implemented with real scraping
        
        except Exception as e:
            logger.error(f"Error scraping {site['name']}: {e}")
        
        return quotes
    
    def _parse_product_page(self, html: str, site: Dict, product_name: str, location: FarmLocation) -> List[PriceQuote]:
        """Parse HTML to extract product information"""
        quotes = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            selectors = site["selectors"]
            
            products = soup.select(selectors["product"])
            
            for product in products[:5]:  # Limit to first 5 results
                try:
                    name_elem = product.select_one(selectors["name"])
                    price_elem = product.select_one(selectors["price"])
                    
                    if not name_elem or not price_elem:
                        continue
                    
                    name = name_elem.get_text(strip=True)
                    price_text = price_elem.get_text(strip=True)
                    
                    # Extract price using regex
                    price_match = re.search(r'\$?(\d+\.?\d*)', price_text)
                    if not price_match:
                        continue
                    
                    base_price = float(price_match.group(1))
                    
                    # Extract unit if available
                    unit_elem = product.select_one(selectors.get("unit", ""))
                    unit = unit_elem.get_text(strip=True) if unit_elem else "each"
                    
                    quote = PriceQuote(
                        supplier=site["name"],
                        base_price=base_price,
                        unit=unit,
                        product_name=name,
                        location=f"{location.city}, {location.state}",
                        source=self.name,
                        reliability_score=0.7,  # Web scraped data is less reliable
                        cached_at=datetime.now(timezone.utc)
                    )
                    quotes.append(quote)
                
                except Exception as e:
                    logger.debug(f"Error parsing product from {site['name']}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing HTML from {site['name']}: {e}")
        
        return quotes

class MockDataSource(DataSource):
    """Mock data source for testing and development"""
    
    def __init__(self):
        super().__init__(
            name="Mock_Data",
            base_url="",
            rate_limit_delay=0.1
        )
    
    async def get_prices(self, product_name: str, location: FarmLocation) -> List[PriceQuote]:
        """Generate realistic mock price data"""
        await self._rate_limit()
        
        # Base prices for common agricultural products (per unit)
        base_prices = {
            "corn seed": 250.0,
            "soybean seed": 45.0,
            "wheat seed": 12.0,
            "fertilizer": 650.0,
            "nitrogen": 0.85,
            "phosphorus": 1.20,
            "potassium": 0.95,
            "diesel fuel": 3.50,
            "pesticide": 25.0,
            "herbicide": 18.0,
            "fungicide": 32.0
        }
        
        # Find base price for product
        normalized_name = product_name.lower().strip()
        base_price = base_prices.get(normalized_name, 100.0)
        
        # Generate multiple quotes with price variation
        quotes = []
        suppliers = [
            "AgriCorp Supply", "FarmTech Solutions", "GreenField Distributors",
            "Midwest Ag Supply", "Prairie Seed Co", "Regional Co-op"
        ]
        
        for i, supplier in enumerate(suppliers):
            # Add realistic price variation (±15%)
            variation = 0.85 + (i * 0.05)  # 0.85 to 1.10 multiplier
            price = base_price * variation
            
            quote = PriceQuote(
                supplier=supplier,
                base_price=round(price, 2),
                unit="per unit" if "seed" in normalized_name else "per gallon" if "fuel" in normalized_name else "per lb",
                product_name=product_name,
                location=f"{location.city}, {location.state}",
                source=self.name,
                moq=50 if i < 2 else None,  # Some suppliers have MOQ
                delivery_terms="FOB" if i % 2 == 0 else "Delivered",
                lead_time=7 + (i * 2),  # 7-17 days
                reliability_score=0.8 + (i * 0.03),  # 0.8-0.95
                contact_info=f"contact@{supplier.lower().replace(' ', '')}.com",
                cached_at=datetime.now(timezone.utc)
            )
            quotes.append(quote)
        
        return quotes

class MarketDataService:
    """
    Main service for collecting agricultural market data from multiple sources.
    Implements caching, data validation, and graceful error handling.
    """
    
    def __init__(self, use_mock_data: bool = True):
        self.cache = MarketDataCache()
        self.use_mock_data = use_mock_data
        
        # Initialize data sources
        self.data_sources = []
        
        if use_mock_data:
            self.data_sources.append(MockDataSource())
        else:
            # Real data sources (commented out for MVP)
            # self.data_sources.append(USDADataSource())
            # self.data_sources.append(AgSupplyWebScraper())
            pass
        
        logger.info(f"MarketDataService initialized with {len(self.data_sources)} data sources")
    
    async def get_current_prices(self, product_name: str, location: FarmLocation, 
                               use_cache: bool = True, max_cache_age_hours: int = 24) -> List[PriceQuote]:
        """
        Get current market prices for a product from all available sources.
        
        Args:
            product_name: Name of the agricultural product
            location: Farm location for regional pricing
            use_cache: Whether to use cached data if available
            max_cache_age_hours: Maximum age of cached data to use
            
        Returns:
            List of price quotes from various sources
        """
        location_str = f"{location.city}, {location.state}"
        
        # Try to get cached data first
        if use_cache:
            cached_data = self.cache.get_cached_market_data(
                product_name, location_str, max_cache_age_hours
            )
            if cached_data and cached_data.get("price_quotes"):
                logger.info(f"Using cached data for {product_name}")
                return [self._dict_to_price_quote(quote) for quote in cached_data["price_quotes"]]
        
        # Fetch fresh data from all sources
        all_quotes = []
        
        for source in self.data_sources:
            try:
                quotes = await source.get_prices(product_name, location)
                validated_quotes = self._validate_quotes(quotes)
                all_quotes.extend(validated_quotes)
                
                logger.info(f"Got {len(validated_quotes)} quotes from {source.name}")
            
            except Exception as e:
                logger.error(f"Error getting data from {source.name}: {e}")
                continue
        
        # Cache the results
        if all_quotes:
            quote_dicts = [quote.to_dict() for quote in all_quotes]
            try:
                self.cache.cache_market_data(product_name, location_str, quote_dicts)
            except StorageError as e:
                logger.error(f"Failed to cache market data: {e}")
        
        return all_quotes
    
    def _validate_quotes(self, quotes: List[PriceQuote]) -> List[PriceQuote]:
        """Validate and clean price quote data"""
        validated = []
        
        for quote in quotes:
            try:
                # Basic validation
                if not quote.supplier or not quote.product_name:
                    continue
                
                if quote.base_price <= 0:
                    continue
                
                # Clean and normalize data
                quote.supplier = quote.supplier.strip()
                quote.product_name = quote.product_name.strip()
                quote.unit = quote.unit.strip() if quote.unit else "each"
                
                # Set reliability score if not provided
                if quote.reliability_score is None:
                    quote.reliability_score = 0.5  # Default moderate reliability
                
                validated.append(quote)
            
            except Exception as e:
                logger.debug(f"Skipping invalid quote: {e}")
                continue
        
        return validated
    
    def _dict_to_price_quote(self, quote_dict: Dict[str, Any]) -> PriceQuote:
        """Convert dictionary back to PriceQuote object"""
        cached_at = None
        if quote_dict.get("cached_at"):
            try:
                cached_at = datetime.fromisoformat(quote_dict["cached_at"])
            except ValueError:
                pass
        
        return PriceQuote(
            supplier=quote_dict["supplier"],
            base_price=quote_dict.get("base_price", quote_dict.get("price", 0.0)),
            unit=quote_dict["unit"],
            product_name=quote_dict["product_name"],
            location=quote_dict["location"],
            source=quote_dict["source"],
            moq=quote_dict.get("moq"),
            delivery_terms=quote_dict.get("delivery_terms"),
            lead_time=quote_dict.get("lead_time"),
            reliability_score=quote_dict.get("reliability_score"),
            contact_info=quote_dict.get("contact_info"),
            specifications=quote_dict.get("specifications"),
            purity_grade=quote_dict.get("purity_grade"),
            pack_size=quote_dict.get("pack_size"),
            promotions=quote_dict.get("promotions"),
            price_breaks=quote_dict.get("price_breaks"),
            cached_at=cached_at
        )
    
    async def get_product_availability(self, product_name: str, location: FarmLocation) -> Dict[str, Any]:
        """
        Check product availability across different sources.
        
        Returns:
            Dictionary with availability information and data quality metrics
        """
        quotes = await self.get_current_prices(product_name, location)
        
        availability_info = {
            "product_name": product_name,
            "location": f"{location.city}, {location.state}",
            "total_sources": len(self.data_sources),
            "sources_with_data": len(set(quote.source for quote in quotes)),
            "total_quotes": len(quotes),
            "price_range": None,
            "average_reliability": 0.0,
            "data_freshness_hours": 0.0,
            "sources": []
        }
        
        if quotes:
            prices = [quote.base_price for quote in quotes]
            availability_info["price_range"] = {
                "min": min(prices),
                "max": max(prices),
                "avg": sum(prices) / len(prices)
            }
            
            # Calculate average reliability
            reliabilities = [quote.reliability_score for quote in quotes if quote.reliability_score]
            if reliabilities:
                availability_info["average_reliability"] = sum(reliabilities) / len(reliabilities)
            
            # Calculate data freshness
            now = datetime.now(timezone.utc)
            freshness_hours = []
            for quote in quotes:
                if quote.cached_at:
                    hours_old = (now - quote.cached_at).total_seconds() / 3600
                    freshness_hours.append(hours_old)
            
            if freshness_hours:
                availability_info["data_freshness_hours"] = sum(freshness_hours) / len(freshness_hours)
            
            # Source breakdown
            source_stats = {}
            for quote in quotes:
                if quote.source not in source_stats:
                    source_stats[quote.source] = {
                        "name": quote.source,
                        "quote_count": 0,
                        "avg_price": 0.0,
                        "avg_reliability": 0.0
                    }
                
                stats = source_stats[quote.source]
                stats["quote_count"] += 1
                stats["avg_price"] = (stats["avg_price"] * (stats["quote_count"] - 1) + quote.base_price) / stats["quote_count"]
                if quote.reliability_score:
                    stats["avg_reliability"] = (stats["avg_reliability"] * (stats["quote_count"] - 1) + quote.reliability_score) / stats["quote_count"]
            
            availability_info["sources"] = list(source_stats.values())
        
        return availability_info
    
    def clear_cache(self) -> int:
        """Clear expired market data cache"""
        try:
            return self.cache.clear_expired_market_data()
        except StorageError as e:
            logger.error(f"Failed to clear cache: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            cache_data = self.cache._read_json_file(self.cache.market_data_file)
            
            total_entries = len(cache_data)
            total_quotes = sum(len(entry.get("price_quotes", [])) for entry in cache_data.values())
            
            # Calculate cache age distribution
            now = datetime.now(timezone.utc)
            age_distribution = {"0-1h": 0, "1-6h": 0, "6-24h": 0, "1d+": 0}
            
            for entry in cache_data.values():
                try:
                    last_updated = datetime.fromisoformat(entry["last_updated"])
                    age_hours = (now - last_updated).total_seconds() / 3600
                    
                    if age_hours < 1:
                        age_distribution["0-1h"] += 1
                    elif age_hours < 6:
                        age_distribution["1-6h"] += 1
                    elif age_hours < 24:
                        age_distribution["6-24h"] += 1
                    else:
                        age_distribution["1d+"] += 1
                except (KeyError, ValueError):
                    age_distribution["1d+"] += 1
            
            return {
                "total_cached_products": total_entries,
                "total_price_quotes": total_quotes,
                "age_distribution": age_distribution,
                "data_sources_count": len(self.data_sources),
                "mock_data_enabled": self.use_mock_data
            }
        
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}

class DataAvailabilityManager:
    """
    Manages data availability reporting and fallback strategies.
    Provides graceful handling when market data is unavailable.
    """
    
    def __init__(self, market_service: MarketDataService):
        self.market_service = market_service
    
    async def get_comprehensive_data_report(self, product_name: str, location: FarmLocation) -> Dict[str, Any]:
        """
        Generate comprehensive data availability report for a product.
        
        Returns:
            Detailed report including data quality, coverage, and limitations
        """
        try:
            # Get price quotes and availability info
            quotes = await self.market_service.get_current_prices(product_name, location)
            availability = await self.market_service.get_product_availability(product_name, location)
            
            # Analyze data quality
            data_quality = self._analyze_data_quality(quotes)
            
            # Identify data gaps and limitations
            limitations = self._identify_data_limitations(quotes, availability)
            
            # Generate fallback recommendations
            fallback_strategies = self._generate_fallback_strategies(product_name, quotes, limitations)
            
            report = {
                "product_name": product_name,
                "location": f"{location.city}, {location.state}",
                "data_availability": {
                    "price_data_found": len(quotes) > 0,
                    "supplier_data_found": any(quote.supplier for quote in quotes),
                    "contact_info_available": any(quote.contact_info for quote in quotes),
                    "delivery_terms_available": any(quote.delivery_terms for quote in quotes),
                    "moq_data_available": any(quote.moq for quote in quotes),
                    "lead_time_available": any(quote.lead_time for quote in quotes)
                },
                "data_quality": data_quality,
                "data_limitations": limitations,
                "fallback_strategies": fallback_strategies,
                "confidence_level": self._calculate_confidence_level(quotes, data_quality),
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating data report for {product_name}: {e}")
            return self._generate_error_report(product_name, location, str(e))
    
    def _analyze_data_quality(self, quotes: List[PriceQuote]) -> Dict[str, Any]:
        """Analyze the quality of available price data"""
        if not quotes:
            return {
                "overall_score": 0.0,
                "quote_count": 0,
                "source_diversity": 0,
                "reliability_score": 0.0,
                "freshness_score": 0.0,
                "completeness_score": 0.0
            }
        
        # Source diversity (more sources = better quality)
        unique_sources = len(set(quote.source for quote in quotes))
        source_diversity_score = min(unique_sources / 3.0, 1.0)  # Normalize to 0-1
        
        # Average reliability
        reliabilities = [quote.reliability_score for quote in quotes if quote.reliability_score]
        avg_reliability = sum(reliabilities) / len(reliabilities) if reliabilities else 0.5
        
        # Data freshness (newer = better)
        now = datetime.now(timezone.utc)
        freshness_scores = []
        for quote in quotes:
            if quote.cached_at:
                hours_old = (now - quote.cached_at).total_seconds() / 3600
                # Score decreases with age: 1.0 for <1h, 0.8 for <6h, 0.6 for <24h, 0.3 for older
                if hours_old < 1:
                    freshness_scores.append(1.0)
                elif hours_old < 6:
                    freshness_scores.append(0.8)
                elif hours_old < 24:
                    freshness_scores.append(0.6)
                else:
                    freshness_scores.append(0.3)
            else:
                freshness_scores.append(0.5)  # Unknown age
        
        avg_freshness = sum(freshness_scores) / len(freshness_scores)
        
        # Data completeness (how much optional data is available)
        completeness_factors = []
        for quote in quotes:
            factors = [
                1.0 if quote.supplier else 0.0,
                1.0 if quote.contact_info else 0.0,
                1.0 if quote.delivery_terms else 0.0,
                1.0 if quote.moq else 0.0,
                1.0 if quote.lead_time else 0.0,
                1.0 if quote.specifications else 0.0
            ]
            completeness_factors.append(sum(factors) / len(factors))
        
        avg_completeness = sum(completeness_factors) / len(completeness_factors)
        
        # Overall quality score (weighted average)
        overall_score = (
            source_diversity_score * 0.3 +
            avg_reliability * 0.3 +
            avg_freshness * 0.2 +
            avg_completeness * 0.2
        )
        
        return {
            "overall_score": round(overall_score, 3),
            "quote_count": len(quotes),
            "source_diversity": unique_sources,
            "reliability_score": round(avg_reliability, 3),
            "freshness_score": round(avg_freshness, 3),
            "completeness_score": round(avg_completeness, 3)
        }
    
    def _identify_data_limitations(self, quotes: List[PriceQuote], availability: Dict[str, Any]) -> List[str]:
        """Identify specific data limitations and gaps"""
        limitations = []
        
        if not quotes:
            limitations.append("No price data available from any source")
            return limitations
        
        # Check for various data gaps
        if len(quotes) < 3:
            limitations.append(f"Limited price data: only {len(quotes)} quote(s) available")
        
        if availability["sources_with_data"] < 2:
            limitations.append("Price data from single source only - limited market coverage")
        
        # Check for missing supplier information
        quotes_with_contact = sum(1 for quote in quotes if quote.contact_info)
        if quotes_with_contact == 0:
            limitations.append("No supplier contact information available")
        elif quotes_with_contact < len(quotes) / 2:
            limitations.append("Limited supplier contact information available")
        
        # Check for missing delivery terms
        quotes_with_delivery = sum(1 for quote in quotes if quote.delivery_terms)
        if quotes_with_delivery == 0:
            limitations.append("No delivery terms information available")
        
        # Check for missing MOQ data
        quotes_with_moq = sum(1 for quote in quotes if quote.moq)
        if quotes_with_moq == 0:
            limitations.append("No minimum order quantity (MOQ) data available")
        
        # Check for missing lead time data
        quotes_with_lead_time = sum(1 for quote in quotes if quote.lead_time)
        if quotes_with_lead_time == 0:
            limitations.append("No lead time information available")
        
        # Check data freshness
        if availability.get("data_freshness_hours", 0) > 48:
            limitations.append("Price data may be outdated (>48 hours old)")
        
        # Check reliability
        if availability.get("average_reliability", 0) < 0.6:
            limitations.append("Low reliability score for available data sources")
        
        return limitations
    
    def _generate_fallback_strategies(self, product_name: str, quotes: List[PriceQuote], 
                                    limitations: List[str]) -> List[Dict[str, Any]]:
        """Generate fallback strategies when data is limited"""
        strategies = []
        
        if not quotes:
            strategies.append({
                "strategy": "manual_research",
                "description": "Conduct manual market research for this product",
                "action_items": [
                    "Contact local agricultural suppliers directly",
                    "Check regional co-op pricing",
                    "Research online agricultural marketplaces",
                    "Consult with other farmers in the area"
                ],
                "priority": "high"
            })
            
            strategies.append({
                "strategy": "similar_product_analysis",
                "description": "Use pricing data from similar agricultural products",
                "action_items": [
                    "Identify comparable products with available data",
                    "Apply price adjustment factors based on product differences",
                    "Use historical price relationships between products"
                ],
                "priority": "medium"
            })
        
        else:
            # Strategies for improving limited data
            if len(quotes) < 3:
                strategies.append({
                    "strategy": "expand_search_radius",
                    "description": "Search for suppliers in nearby regions",
                    "action_items": [
                        "Include suppliers from neighboring states",
                        "Consider regional distributors",
                        "Check national suppliers with local delivery"
                    ],
                    "priority": "medium"
                })
            
            if "No supplier contact information available" in limitations:
                strategies.append({
                    "strategy": "direct_supplier_contact",
                    "description": "Obtain direct contact information for price verification",
                    "action_items": [
                        "Visit supplier websites for contact details",
                        "Call main business numbers for pricing departments",
                        "Request quotes directly via email or online forms"
                    ],
                    "priority": "high"
                })
            
            if "No delivery terms information available" in limitations:
                strategies.append({
                    "strategy": "delivery_cost_estimation",
                    "description": "Estimate delivery costs based on location and product type",
                    "action_items": [
                        "Use standard freight calculators",
                        "Apply typical delivery cost percentages for product category",
                        "Factor in fuel surcharges and handling fees"
                    ],
                    "priority": "medium"
                })
            
            if any("outdated" in limitation for limitation in limitations):
                strategies.append({
                    "strategy": "price_trend_adjustment",
                    "description": "Adjust outdated prices using market trend data",
                    "action_items": [
                        "Apply commodity price index adjustments",
                        "Use inflation factors for price updates",
                        "Check recent market reports for price movements"
                    ],
                    "priority": "medium"
                })
        
        return strategies
    
    def _calculate_confidence_level(self, quotes: List[PriceQuote], data_quality: Dict[str, Any]) -> str:
        """Calculate overall confidence level for the analysis"""
        if not quotes:
            return "very_low"
        
        overall_score = data_quality.get("overall_score", 0.0)
        quote_count = len(quotes)
        
        if overall_score >= 0.8 and quote_count >= 5:
            return "high"
        elif overall_score >= 0.6 and quote_count >= 3:
            return "medium"
        elif overall_score >= 0.4 and quote_count >= 2:
            return "low"
        else:
            return "very_low"
    
    def _generate_error_report(self, product_name: str, location: FarmLocation, error_msg: str) -> Dict[str, Any]:
        """Generate error report when data collection fails"""
        return {
            "product_name": product_name,
            "location": f"{location.city}, {location.state}",
            "data_availability": {
                "price_data_found": False,
                "supplier_data_found": False,
                "contact_info_available": False,
                "delivery_terms_available": False,
                "moq_data_available": False,
                "lead_time_available": False
            },
            "data_quality": {
                "overall_score": 0.0,
                "quote_count": 0,
                "source_diversity": 0,
                "reliability_score": 0.0,
                "freshness_score": 0.0,
                "completeness_score": 0.0
            },
            "data_limitations": [
                "Data collection failed due to technical error",
                f"Error details: {error_msg}"
            ],
            "fallback_strategies": [
                {
                    "strategy": "manual_research",
                    "description": "Conduct manual market research due to system error",
                    "action_items": [
                        "Contact suppliers directly by phone or email",
                        "Visit local agricultural supply stores",
                        "Check online marketplaces manually"
                    ],
                    "priority": "high"
                }
            ],
            "confidence_level": "very_low",
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "error": True
        }

class PartialAnalysisHandler:
    """
    Handles partial analysis when only some data sources are available.
    Provides meaningful results even with incomplete data.
    """
    
    def __init__(self, market_service: MarketDataService):
        self.market_service = market_service
        self.availability_manager = DataAvailabilityManager(market_service)
    
    async def perform_partial_analysis(self, products: List[str], location: FarmLocation) -> Dict[str, Any]:
        """
        Perform analysis on multiple products with graceful handling of missing data.
        
        Args:
            products: List of product names to analyze
            location: Farm location for regional pricing
            
        Returns:
            Analysis results with data availability reporting
        """
        results = {
            "total_products": len(products),
            "successful_analyses": 0,
            "partial_analyses": 0,
            "failed_analyses": 0,
            "product_results": [],
            "overall_data_quality": {
                "average_confidence": 0.0,
                "data_coverage_percentage": 0.0,
                "reliable_products": [],
                "limited_data_products": [],
                "no_data_products": []
            },
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        confidence_scores = []
        
        for product_name in products:
            try:
                # Get comprehensive data report for each product
                data_report = await self.availability_manager.get_comprehensive_data_report(
                    product_name, location
                )
                
                # Classify the analysis result
                confidence = data_report.get("confidence_level", "very_low")
                has_price_data = data_report.get("data_availability", {}).get("price_data_found", False)
                
                if confidence in ["high", "medium"] and has_price_data:
                    results["successful_analyses"] += 1
                    results["overall_data_quality"]["reliable_products"].append(product_name)
                    confidence_scores.append(0.8 if confidence == "high" else 0.6)
                
                elif confidence in ["low"] and has_price_data:
                    results["partial_analyses"] += 1
                    results["overall_data_quality"]["limited_data_products"].append(product_name)
                    confidence_scores.append(0.4)
                
                else:
                    results["failed_analyses"] += 1
                    results["overall_data_quality"]["no_data_products"].append(product_name)
                    confidence_scores.append(0.0)
                
                # Add product result
                product_result = {
                    "product_name": product_name,
                    "analysis_status": self._determine_analysis_status(confidence, has_price_data),
                    "data_report": data_report,
                    "usable_for_budgeting": confidence in ["high", "medium", "low"] and has_price_data
                }
                
                results["product_results"].append(product_result)
            
            except Exception as e:
                logger.error(f"Error analyzing {product_name}: {e}")
                results["failed_analyses"] += 1
                results["overall_data_quality"]["no_data_products"].append(product_name)
                confidence_scores.append(0.0)
                
                # Add error result
                error_result = {
                    "product_name": product_name,
                    "analysis_status": "error",
                    "data_report": self.availability_manager._generate_error_report(
                        product_name, location, str(e)
                    ),
                    "usable_for_budgeting": False
                }
                results["product_results"].append(error_result)
        
        # Calculate overall metrics
        if confidence_scores:
            results["overall_data_quality"]["average_confidence"] = sum(confidence_scores) / len(confidence_scores)
        
        successful_count = results["successful_analyses"] + results["partial_analyses"]
        results["overall_data_quality"]["data_coverage_percentage"] = (successful_count / len(products)) * 100
        
        return results
    
    def _determine_analysis_status(self, confidence: str, has_price_data: bool) -> str:
        """Determine the analysis status based on confidence and data availability"""
        if not has_price_data:
            return "no_data"
        
        if confidence == "high":
            return "complete"
        elif confidence == "medium":
            return "good"
        elif confidence == "low":
            return "limited"
        else:
            return "poor"
    
    async def generate_budget_recommendations(self, partial_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate budget recommendations based on partial analysis results.
        Provides guidance on how to proceed with incomplete data.
        """
        recommendations = {
            "budgeting_approach": "",
            "confidence_level": "",
            "recommended_actions": [],
            "risk_factors": [],
            "alternative_strategies": []
        }
        
        reliable_count = len(partial_results["overall_data_quality"]["reliable_products"])
        limited_count = len(partial_results["overall_data_quality"]["limited_data_products"])
        no_data_count = len(partial_results["overall_data_quality"]["no_data_products"])
        total_count = partial_results["total_products"]
        
        coverage_percentage = partial_results["overall_data_quality"]["data_coverage_percentage"]
        
        # Determine budgeting approach
        if coverage_percentage >= 80:
            recommendations["budgeting_approach"] = "standard"
            recommendations["confidence_level"] = "high"
            recommendations["recommended_actions"].append(
                "Proceed with budget planning using available data"
            )
        
        elif coverage_percentage >= 60:
            recommendations["budgeting_approach"] = "conservative"
            recommendations["confidence_level"] = "medium"
            recommendations["recommended_actions"].extend([
                "Add 10-15% buffer to budget estimates for uncertainty",
                "Prioritize products with reliable data for immediate planning"
            ])
        
        elif coverage_percentage >= 30:
            recommendations["budgeting_approach"] = "high_uncertainty"
            recommendations["confidence_level"] = "low"
            recommendations["recommended_actions"].extend([
                "Add 20-30% buffer to budget estimates",
                "Focus on manual research for products with no data",
                "Consider phased purchasing approach"
            ])
        
        else:
            recommendations["budgeting_approach"] = "manual_research_required"
            recommendations["confidence_level"] = "very_low"
            recommendations["recommended_actions"].extend([
                "Conduct extensive manual market research",
                "Contact multiple suppliers directly for quotes",
                "Consider delaying budget finalization until more data is available"
            ])
        
        # Add risk factors
        if no_data_count > 0:
            recommendations["risk_factors"].append(
                f"{no_data_count} product(s) have no pricing data - budget may be significantly incomplete"
            )
        
        if limited_count > total_count * 0.3:
            recommendations["risk_factors"].append(
                "High proportion of products have limited data quality - price estimates may be inaccurate"
            )
        
        # Add alternative strategies
        if coverage_percentage < 70:
            recommendations["alternative_strategies"].extend([
                "Consider grouping similar products for bulk purchasing",
                "Explore regional cooperative purchasing programs",
                "Investigate alternative suppliers or product substitutes"
            ])
        
        return recommendations

# Enhanced MarketDataService with graceful data handling
class EnhancedMarketDataService(MarketDataService):
    """
    Enhanced version of MarketDataService with comprehensive data handling capabilities.
    Includes fallback strategies, partial analysis, and detailed reporting.
    """
    
    def __init__(self, use_mock_data: bool = True):
        super().__init__(use_mock_data)
        self.availability_manager = DataAvailabilityManager(self)
        self.partial_handler = PartialAnalysisHandler(self)
    
    async def analyze_product_list_with_fallbacks(self, products: List[str], 
                                                location: FarmLocation) -> Dict[str, Any]:
        """
        Analyze a list of products with comprehensive fallback handling.
        
        Returns complete analysis with data availability reporting and recommendations.
        """
        try:
            # Perform partial analysis
            partial_results = await self.partial_handler.perform_partial_analysis(products, location)
            
            # Generate budget recommendations
            budget_recommendations = await self.partial_handler.generate_budget_recommendations(partial_results)
            
            # Combine results
            enhanced_results = {
                "analysis_results": partial_results,
                "budget_recommendations": budget_recommendations,
                "data_quality_summary": {
                    "overall_confidence": partial_results["overall_data_quality"]["average_confidence"],
                    "data_coverage": partial_results["overall_data_quality"]["data_coverage_percentage"],
                    "products_with_reliable_data": len(partial_results["overall_data_quality"]["reliable_products"]),
                    "products_needing_manual_research": len(partial_results["overall_data_quality"]["no_data_products"])
                },
                "next_steps": self._generate_next_steps(partial_results, budget_recommendations)
            }
            
            return enhanced_results
        
        except Exception as e:
            logger.error(f"Error in enhanced analysis: {e}")
            return {
                "error": True,
                "message": f"Analysis failed: {str(e)}",
                "fallback_recommendation": "Conduct manual market research for all products"
            }
    
    def _generate_next_steps(self, partial_results: Dict[str, Any], 
                           budget_recommendations: Dict[str, Any]) -> List[str]:
        """Generate actionable next steps based on analysis results"""
        next_steps = []
        
        # Steps based on data availability
        no_data_products = partial_results["overall_data_quality"]["no_data_products"]
        if no_data_products:
            next_steps.append(
                f"Research pricing for {len(no_data_products)} product(s) with no data: {', '.join(no_data_products[:3])}"
                + ("..." if len(no_data_products) > 3 else "")
            )
        
        limited_data_products = partial_results["overall_data_quality"]["limited_data_products"]
        if limited_data_products:
            next_steps.append(
                f"Verify pricing for {len(limited_data_products)} product(s) with limited data"
            )
        
        # Steps based on budget recommendations
        if budget_recommendations["confidence_level"] in ["low", "very_low"]:
            next_steps.append("Add significant buffer (20-30%) to budget estimates due to data uncertainty")
        
        # General next steps
        next_steps.extend([
            "Contact suppliers directly for current quotes and delivery terms",
            "Review and update budget estimates as more data becomes available"
        ])
        
        return next_steps