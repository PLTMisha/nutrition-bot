"""
Open Food Facts API service for product information
"""
import logging
import asyncio
from typing import Optional, Dict, Any, List
from urllib.parse import quote

import aiohttp
from aiohttp import ClientTimeout, ClientError

from config.settings import OPENFOODFACTS_CONFIG
from utils.cache import cache_result

logger = logging.getLogger(__name__)


class OpenFoodFactsService:
    """Service for interacting with Open Food Facts API"""
    
    def __init__(self):
        self.base_url = OPENFOODFACTS_CONFIG["base_url"]
        self.user_agent = OPENFOODFACTS_CONFIG["user_agent"]
        self.timeout = ClientTimeout(total=OPENFOODFACTS_CONFIG["timeout"])
        self.max_retries = OPENFOODFACTS_CONFIG["retries"]
    
    async def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request with retry logic"""
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json"
        }
        
        for attempt in range(self.max_retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 404:
                            logger.warning(f"Product not found: {url}")
                            return None
                        else:
                            logger.warning(f"HTTP {response.status} for {url}")
                            
            except asyncio.TimeoutError:
                logger.warning(f"Timeout for request to {url} (attempt {attempt + 1})")
            except ClientError as e:
                logger.warning(f"Client error for {url}: {e} (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Unexpected error for {url}: {e} (attempt {attempt + 1})")
            
            if attempt < self.max_retries:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error(f"Failed to fetch data from {url} after {self.max_retries + 1} attempts")
        return None
    
    @cache_result(ttl=3600)  # Cache for 1 hour
    async def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get product information by barcode"""
        if not barcode or not barcode.isdigit():
            logger.warning(f"Invalid barcode: {barcode}")
            return None
        
        url = f"{self.base_url}/v2/product/{barcode}.json"
        
        try:
            data = await self._make_request(url)
            
            if not data or data.get("status") != 1:
                logger.info(f"Product not found for barcode: {barcode}")
                return None
            
            product = data.get("product", {})
            return self._parse_product_data(product, barcode)
            
        except Exception as e:
            logger.error(f"Error fetching product by barcode {barcode}: {e}")
            return None
    
    @cache_result(ttl=1800)  # Cache for 30 minutes
    async def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search products by name"""
        if not query or len(query.strip()) < 2:
            logger.warning(f"Invalid search query: {query}")
            return []
        
        # Clean and encode query
        clean_query = query.strip().lower()
        encoded_query = quote(clean_query)
        
        url = f"{self.base_url}/cgi/search.pl"
        params = {
            "search_terms": encoded_query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": min(limit, 50),  # API limit
            "fields": "code,product_name,brands,nutriments,image_url,categories"
        }
        
        try:
            data = await self._make_request(url, params)
            
            if not data or not data.get("products"):
                logger.info(f"No products found for query: {query}")
                return []
            
            products = []
            for product_data in data["products"][:limit]:
                parsed_product = self._parse_product_data(product_data)
                if parsed_product:
                    products.append(parsed_product)
            
            logger.info(f"Found {len(products)} products for query: {query}")
            return products
            
        except Exception as e:
            logger.error(f"Error searching products for query '{query}': {e}")
            return []
    
    def _parse_product_data(self, product_data: Dict, barcode: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Parse product data from Open Food Facts format"""
        try:
            # Basic product info
            name = product_data.get("product_name") or product_data.get("product_name_en")
            if not name:
                # Try alternative name fields
                name = (
                    product_data.get("generic_name") or
                    product_data.get("abbreviated_product_name") or
                    "Unknown Product"
                )
            
            brand = product_data.get("brands", "").split(",")[0].strip() if product_data.get("brands") else None
            code = barcode or product_data.get("code")
            
            # Nutrition data (per 100g)
            nutriments = product_data.get("nutriments", {})
            
            # Extract nutrition values with fallbacks
            calories = self._extract_nutrition_value(nutriments, ["energy-kcal_100g", "energy_100g"], conversion_factor=0.239006)  # kJ to kcal
            proteins = self._extract_nutrition_value(nutriments, ["proteins_100g"])
            fats = self._extract_nutrition_value(nutriments, ["fat_100g"])
            carbs = self._extract_nutrition_value(nutriments, ["carbohydrates_100g"])
            
            # Additional nutrition info
            fiber = self._extract_nutrition_value(nutriments, ["fiber_100g"])
            sugar = self._extract_nutrition_value(nutriments, ["sugars_100g"])
            sodium = self._extract_nutrition_value(nutriments, ["sodium_100g"])
            
            # Validate essential nutrition data
            if calories is None and proteins is None and fats is None and carbs is None:
                logger.warning(f"No nutrition data found for product: {name}")
                return None
            
            # Set defaults for missing values
            calories = calories or 0
            proteins = proteins or 0
            fats = fats or 0
            carbs = carbs or 0
            
            # Additional metadata
            categories = product_data.get("categories", "")
            image_url = product_data.get("image_url") or product_data.get("image_front_url")
            
            # Data quality score (based on completeness)
            quality_score = self._calculate_quality_score(product_data, nutriments)
            
            return {
                "name": name.strip(),
                "brand": brand,
                "barcode": code,
                "calories_per_100g": float(calories),
                "proteins_per_100g": float(proteins),
                "fats_per_100g": float(fats),
                "carbs_per_100g": float(carbs),
                "fiber_per_100g": float(fiber) if fiber is not None else None,
                "sugar_per_100g": float(sugar) if sugar is not None else None,
                "sodium_per_100g": float(sodium) if sodium is not None else None,
                "category": categories.split(",")[0].strip() if categories else None,
                "image_url": image_url,
                "source": "openfoodfacts",
                "data_quality_score": quality_score
            }
            
        except Exception as e:
            logger.error(f"Error parsing product data: {e}")
            return None
    
    def _extract_nutrition_value(self, nutriments: Dict, keys: List[str], conversion_factor: float = 1.0) -> Optional[float]:
        """Extract nutrition value from nutriments with fallback keys"""
        for key in keys:
            value = nutriments.get(key)
            if value is not None:
                try:
                    return float(value) * conversion_factor
                except (ValueError, TypeError):
                    continue
        return None
    
    def _calculate_quality_score(self, product_data: Dict, nutriments: Dict) -> float:
        """Calculate data quality score (0-1)"""
        score = 0.0
        max_score = 10.0
        
        # Basic info completeness
        if product_data.get("product_name"):
            score += 2.0
        if product_data.get("brands"):
            score += 1.0
        if product_data.get("categories"):
            score += 1.0
        if product_data.get("image_url"):
            score += 1.0
        
        # Nutrition completeness
        nutrition_fields = ["energy-kcal_100g", "proteins_100g", "fat_100g", "carbohydrates_100g"]
        for field in nutrition_fields:
            if nutriments.get(field) is not None:
                score += 1.0
        
        # Additional nutrition data
        if nutriments.get("fiber_100g") is not None:
            score += 0.5
        if nutriments.get("sodium_100g") is not None:
            score += 0.5
        
        return min(score / max_score, 1.0)
    
    async def get_popular_products(self, category: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get popular products, optionally filtered by category"""
        url = f"{self.base_url}/cgi/search.pl"
        params = {
            "action": "process",
            "json": 1,
            "page_size": limit,
            "sort_by": "popularity",
            "fields": "code,product_name,brands,nutriments,image_url,categories"
        }
        
        if category:
            params["tagtype_0"] = "categories"
            params["tag_contains_0"] = "contains"
            params["tag_0"] = category
        
        try:
            data = await self._make_request(url, params)
            
            if not data or not data.get("products"):
                return []
            
            products = []
            for product_data in data["products"]:
                parsed_product = self._parse_product_data(product_data)
                if parsed_product:
                    products.append(parsed_product)
            
            return products
            
        except Exception as e:
            logger.error(f"Error fetching popular products: {e}")
            return []
    
    async def get_product_suggestions(self, partial_name: str, limit: int = 5) -> List[str]:
        """Get product name suggestions for autocomplete"""
        if len(partial_name.strip()) < 2:
            return []
        
        try:
            products = await self.search_products(partial_name, limit=limit * 2)
            
            # Extract unique product names
            suggestions = []
            seen_names = set()
            
            for product in products:
                name = product["name"].lower()
                if name not in seen_names and partial_name.lower() in name:
                    suggestions.append(product["name"])
                    seen_names.add(name)
                    
                    if len(suggestions) >= limit:
                        break
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting product suggestions: {e}")
            return []
    
    async def validate_barcode(self, barcode: str) -> bool:
        """Validate if barcode exists in Open Food Facts"""
        try:
            product = await self.get_product_by_barcode(barcode)
            return product is not None
        except Exception:
            return False
    
    def calculate_nutrition_for_quantity(self, product: Dict[str, Any], quantity_g: float) -> Dict[str, float]:
        """Calculate nutrition values for specific quantity"""
        multiplier = quantity_g / 100.0
        
        return {
            "calories": product["calories_per_100g"] * multiplier,
            "proteins": product["proteins_per_100g"] * multiplier,
            "fats": product["fats_per_100g"] * multiplier,
            "carbs": product["carbs_per_100g"] * multiplier,
            "fiber": product.get("fiber_per_100g", 0) * multiplier if product.get("fiber_per_100g") else None,
            "sugar": product.get("sugar_per_100g", 0) * multiplier if product.get("sugar_per_100g") else None,
            "sodium": product.get("sodium_per_100g", 0) * multiplier if product.get("sodium_per_100g") else None,
        }


# Global service instance
openfoodfacts_service = OpenFoodFactsService()
