"""
Vercel API service for image processing functions
RAILWAY EMERGENCY FIX: Updated 2025-09-06 14:46 - REMOVED PROBLEMATIC FUNCTION ENTIRELY
"""
import logging
import asyncio
import base64
from typing import Optional, Dict, Any, Union
from io import BytesIO

import aiohttp
from aiohttp import ClientTimeout, ClientError
from PIL import Image

from config.settings import VERCEL_CONFIG, IMAGE_CONFIG

logger = logging.getLogger(__name__)


class VercelAPIService:
    """Service for interacting with Vercel serverless functions"""
    
    def __init__(self):
        self.base_url = VERCEL_CONFIG["base_url"]
        self.api_key = VERCEL_CONFIG["api_key"]
        self.timeout = ClientTimeout(total=VERCEL_CONFIG["timeout"])
        self.max_retries = VERCEL_CONFIG["retries"]
    
    async def _make_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        method: str = "POST"
    ) -> Optional[Dict[str, Any]]:
        """Make HTTP request to Vercel function"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        for attempt in range(self.max_retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.request(method, url, json=data, headers=headers) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 400:
                            error_data = await response.json()
                            logger.warning(f"Bad request to {endpoint}: {error_data}")
                            return {"error": error_data.get("message", "Bad request")}
                        elif response.status == 500:
                            logger.warning(f"Server error for {endpoint} (attempt {attempt + 1})")
                        else:
                            logger.warning(f"HTTP {response.status} for {endpoint}")
                            
            except asyncio.TimeoutError:
                logger.warning(f"Timeout for {endpoint} (attempt {attempt + 1})")
            except ClientError as e:
                logger.warning(f"Client error for {endpoint}: {e} (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Unexpected error for {endpoint}: {e} (attempt {attempt + 1})")
            
            if attempt < self.max_retries:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error(f"Failed to call {endpoint} after {self.max_retries + 1} attempts")
        return {"error": "Service temporarily unavailable"}
    
    def _prepare_image_data(self, image_data: bytes) -> Optional[str]:
        """Prepare image data for API call"""
        try:
            # Validate image size
            if len(image_data) > IMAGE_CONFIG["max_size"]:
                logger.warning(f"Image too large: {len(image_data)} bytes")
                return None
            
            # Validate and potentially resize image
            try:
                image = Image.open(BytesIO(image_data))
                
                # Check if resize is needed
                max_width = IMAGE_CONFIG["max_width"]
                max_height = IMAGE_CONFIG["max_height"]
                
                if image.width > max_width or image.height > max_height:
                    # Calculate new dimensions maintaining aspect ratio
                    ratio = min(max_width / image.width, max_height / image.height)
                    new_width = int(image.width * ratio)
                    new_height = int(image.height * ratio)
                    
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Convert back to bytes
                    output = BytesIO()
                    image.save(output, format='JPEG', quality=IMAGE_CONFIG["quality"])
                    image_data = output.getvalue()
                    
                    logger.info(f"Resized image to {new_width}x{new_height}")
            
            except Exception as e:
                logger.warning(f"Error processing image: {e}")
                # Continue with original image data
            
            # Encode to base64
            return base64.b64encode(image_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error preparing image data: {e}")
            return None
    
    async def analyze_photo(
        self,
        image_data: bytes,
        user_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze food photo using GPT-4 Vision and OpenCV"""
        try:
            # Prepare image data
            base64_image = self._prepare_image_data(image_data)
            if not base64_image:
                return {"error": "Invalid image data"}
            
            # Prepare request data
            request_data = {
                "image": base64_image,
                "user_prompt": user_prompt or "Analyze this food photo and estimate portion size"
            }
            
            # Call Vercel function
            response = await self._make_request("analyze-photo", request_data)
            
            if not response:
                return {"error": "No response from analysis service"}
            
            if "error" in response:
                return response
            
            # Validate response structure
            required_fields = ["food_items", "reference_object", "estimated_weight"]
            if not all(field in response for field in required_fields):
                logger.warning(f"Incomplete response from analyze-photo: {response}")
                return {"error": "Incomplete analysis response"}
            
            logger.info(f"Successfully analyzed photo: {len(response.get('food_items', []))} items found")
            return response
            
        except Exception as e:
            logger.error(f"Error in analyze_photo: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def process_barcode(self, image_data: bytes) -> Dict[str, Any]:
        """Process barcode image using pyzbar"""
        try:
            # Prepare image data
            base64_image = self._prepare_image_data(image_data)
            if not base64_image:
                return {"error": "Invalid image data"}
            
            # Prepare request data
            request_data = {
                "image": base64_image
            }
            
            # Call Vercel function
            response = await self._make_request("process-barcode", request_data)
            
            if not response:
                return {"error": "No response from barcode service"}
            
            if "error" in response:
                return response
            
            # Validate response
            if "barcode" not in response:
                return {"error": "No barcode found in image"}
            
            logger.info(f"Successfully processed barcode: {response.get('barcode')}")
            return response
            
        except Exception as e:
            logger.error(f"Error in process_barcode: {e}")
            return {"error": f"Barcode processing failed: {str(e)}"}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of Vercel functions"""
        try:
            response = await self._make_request("health", {}, method="GET")
            
            if response and "status" in response:
                return response
            else:
                return {"status": "unhealthy", "error": "Invalid response"}
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    def is_available(self) -> bool:
        """Check if Vercel API is configured and available"""
        return bool(self.base_url and self.base_url != "https://your-vercel-app.vercel.app")
    
    async def get_supported_reference_objects(self) -> Dict[str, Dict[str, float]]:
        """Get list of supported reference objects with their dimensions"""
        return {
            "coins": {
                "1_euro": {"diameter": 23.25, "name": "Монета 1 евро"},
                "2_euro": {"diameter": 25.75, "name": "Монета 2 евро"}
            },
            "utensils": {
                "tablespoon": {"length": 200, "name": "Столовая ложка"},
                "teaspoon": {"length": 130, "name": "Чайная ложка"},
                "fork": {"length": 200, "name": "Столовая вилка"},
                "knife": {"length": 220, "name": "Столовый нож"}
            },
            "dishes": {
                "plate": {"diameter": 240, "name": "Стандартная тарелка"},
                "saucer": {"diameter": 150, "name": "Блюдце"},
                "cup": {"height": 90, "diameter": 80, "name": "Чашка/кружка"},
                "glass": {"height": 105, "diameter": 73, "name": "Граненый стакан"}
            },
            "objects": {
                "credit_card": {"length": 85.6, "width": 53.98, "name": "Кредитная карта"},
                "matchbox": {"length": 50, "width": 35, "name": "Спичечный коробок"},
                "lighter": {"length": 80.5, "width": 25.5, "name": "Зажигалка BIC"}
            }
        }
    
    def format_analysis_result(self, analysis_result: Dict[str, Any]) -> str:
        """Format analysis result for user display"""
        if "error" in analysis_result:
            return f"❌ Ошибка анализа: {analysis_result['error']}"
        
        try:
            food_items = analysis_result.get("food_items", [])
            reference_object = analysis_result.get("reference_object", {})
            confidence = analysis_result.get("confidence", 0)
            
            if not food_items:
                return "🤔 На фото не удалось распознать блюда"
            
            result_text = "🍽️ <b>Анализ фотографии:</b>\n\n"
            
            # Reference object info
            if reference_object:
                obj_name = reference_object.get("name", "неизвестный объект")
                result_text += f"📏 <b>Эталонный объект:</b> {obj_name}\n"
                if "confidence" in reference_object:
                    result_text += f"🎯 <b>Уверенность:</b> {reference_object['confidence']:.0%}\n"
                result_text += "\n"
            
            # Food items
            for i, item in enumerate(food_items, 1):
                name = item.get("name", f"Блюдо {i}")
                weight = item.get("estimated_weight", 0)
                item_confidence = item.get("confidence", 0)
                
                result_text += f"🍽️ <b>{name}</b>\n"
                result_text += f"⚖️ Примерный вес: {weight:.0f}г\n"
                result_text += f"🎯 Уверенность: {item_confidence:.0%}\n\n"
            
            # Overall confidence
            result_text += f"📊 <b>Общая точность анализа:</b> {confidence:.0%}\n\n"
            result_text += "💡 <i>Вы можете скорректировать вес перед добавлением</i>"
            
            return result_text
            
        except Exception as e:
            logger.error(f"Error formatting analysis result: {e}")
            return "❌ Ошибка при обработке результата анализа"
    
    # TEMPORARY: Function removed due to Railway cache issues
    # Will be restored after deployment works


# Global service instance
vercel_api_service = VercelAPIService()
