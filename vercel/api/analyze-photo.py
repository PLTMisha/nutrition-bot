"""
Vercel function for analyzing food photos using Langdock API (ChatGPT) and OpenCV
"""
import json
import base64
import os
import logging
from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple
import requests

from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Langdock API configuration
LANGDOCK_API_KEY = os.environ.get("LANGDOCK_API_KEY")
LANGDOCK_BASE_URL = os.environ.get("LANGDOCK_BASE_URL", "https://api.langdock.com/v1")

# Reference objects with their real-world dimensions (in mm)
REFERENCE_OBJECTS = {
    "1_euro_coin": {"diameter": 23.25, "name": "Монета 1 евро"},
    "2_euro_coin": {"diameter": 25.75, "name": "Монета 2 евро"},
    "tablespoon": {"length": 200, "name": "Столовая ложка"},
    "teaspoon": {"length": 130, "name": "Чайная ложка"},
    "fork": {"length": 200, "name": "Столовая вилка"},
    "knife": {"length": 220, "name": "Столовый нож"},
    "plate": {"diameter": 240, "name": "Стандартная тарелка"},
    "saucer": {"diameter": 150, "name": "Блюдце"},
    "cup": {"height": 90, "diameter": 80, "name": "Чашка/кружка"},
    "glass": {"height": 105, "diameter": 73, "name": "Граненый стакан"},
    "credit_card": {"length": 85.6, "width": 53.98, "name": "Кредитная карта"},
    "matchbox": {"length": 50, "width": 35, "name": "Спичечный коробок"},
    "lighter": {"length": 80.5, "width": 25.5, "name": "Зажигалка BIC"}
}


def analyze_with_langdock_vision(image_base64: str, user_prompt: str) -> Dict[str, Any]:
    """Analyze image using Langdock API (ChatGPT with vision)"""
    try:
        if not LANGDOCK_API_KEY:
            return {"error": "Langdock API key not configured"}
        
        system_prompt = """
Ты эксперт по анализу фотографий еды. Твоя задача:

1. Определить все блюда/продукты на фото
2. Найти эталонный объект для масштаба (монета, ложка, тарелка, кредитная карта и т.д.)
3. Оценить примерный вес каждого блюда в граммах
4. Дать примерную оценку БЖУ и калорий

Эталонные объекты и их размеры:
- Монета 1€: диаметр 23.25мм
- Монета 2€: диаметр 25.75мм  
- Столовая ложка: длина 20см
- Чайная ложка: длина 13см
- Столовая вилка: длина 20см
- Столовый нож: длина 22см
- Стандартная тарелка: диаметр 24см
- Блюдце: диаметр 15см
- Чашка/кружка: высота 9см, диаметр 8см
- Граненый стакан: высота 10.5см, диаметр 7.3см
- Кредитная карта: 85.6×53.98мм
- Спичечный коробок: 50×35мм
- Зажигалка BIC: 80.5×25.5мм

Отвечай ТОЛЬКО в формате JSON:
{
  "food_items": [
    {
      "name": "название блюда",
      "estimated_weight": вес_в_граммах,
      "confidence": уверенность_от_0_до_1,
      "nutrition_estimate": {
        "calories": калории,
        "proteins": белки_г,
        "fats": жиры_г,
        "carbs": углеводы_г
      }
    }
  ],
  "reference_object": {
    "type": "тип_объекта",
    "name": "название",
    "confidence": уверенность_от_0_до_1,
    "pixel_size": размер_в_пикселях
  },
  "estimated_weight": общий_вес_всех_блюд,
  "confidence": общая_уверенность_анализа,
  "scale_factor": коэффициент_масштаба_пиксель_к_мм
}
        """
        
        # Prepare request payload for Langdock
        payload = {
            "model": "gpt-4-vision-preview",  # или другая модель с поддержкой изображений
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        # Make request to Langdock API
        headers = {
            "Authorization": f"Bearer {LANGDOCK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{LANGDOCK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Langdock API error: {response.status_code} - {response.text}")
            return {"error": f"Langdock API error: {response.status_code}"}
        
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        
        # Try to parse JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # If JSON parsing fails, extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("No valid JSON found in response")
                
    except requests.exceptions.RequestException as e:
        logger.error(f"Langdock API request failed: {e}")
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Langdock Vision analysis failed: {e}")
        return {"error": f"AI analysis failed: {str(e)}"}


def analyze_with_fallback_text(user_prompt: str, image_description: str = "") -> Dict[str, Any]:
    """Fallback analysis using text-only model if vision is not available"""
    try:
        if not LANGDOCK_API_KEY:
            return {"error": "Langdock API key not configured"}
        
        fallback_prompt = f"""
Пользователь отправил фото еды с описанием: "{user_prompt}"
{f"Дополнительное описание изображения: {image_description}" if image_description else ""}

Поскольку анализ изображения недоступен, дай общие рекомендации по БЖУ для типичных блюд.

Отвечай в формате JSON:
{{
  "food_items": [
    {{
      "name": "предполагаемое блюдо",
      "estimated_weight": примерный_вес_в_граммах,
      "confidence": 0.3,
      "nutrition_estimate": {{
        "calories": примерные_калории,
        "proteins": примерные_белки_г,
        "fats": примерные_жиры_г,
        "carbs": примерные_углеводы_г
      }}
    }}
  ],
  "reference_object": {{
    "type": "unknown",
    "name": "Эталонный объект не найден",
    "confidence": 0.0
  }},
  "estimated_weight": общий_примерный_вес,
  "confidence": 0.3,
  "note": "Анализ выполнен без изображения, данные приблизительные"
}}
        """
        
        payload = {
            "model": "gpt-3.5-turbo",  # Используем текстовую модель
            "messages": [
                {"role": "user", "content": fallback_prompt}
            ],
            "max_tokens": 800,
            "temperature": 0.1
        }
        
        headers = {
            "Authorization": f"Bearer {LANGDOCK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{LANGDOCK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            return {"error": f"Langdock API error: {response.status_code}"}
        
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "Could not parse AI response"}
                
    except Exception as e:
        logger.error(f"Fallback analysis failed: {e}")
        return {"error": f"Fallback analysis failed: {str(e)}"}


def detect_reference_object_simple(image_pil: Image.Image) -> Optional[Dict[str, Any]]:
    """Simple reference object detection using PIL only"""
    try:
        # For now, return None - OpenCV functionality disabled
        # In the future, could implement basic detection using PIL
        logger.info("OpenCV detection disabled - using AI-only analysis")
        return None
        
    except Exception as e:
        logger.error(f"Simple detection failed: {e}")
        return None


def process_image(image_base64: str, user_prompt: str) -> Dict[str, Any]:
    """Main image processing function - simplified without OpenCV"""
    try:
        # Decode base64 image for basic validation
        image_data = base64.b64decode(image_base64)
        image_pil = Image.open(BytesIO(image_data))
        
        # Try Langdock Vision analysis first
        langdock_result = analyze_with_langdock_vision(image_base64, user_prompt)
        
        # If vision analysis failed, try fallback
        if "error" in langdock_result:
            logger.warning(f"Vision analysis failed: {langdock_result['error']}")
            # Try fallback text analysis
            langdock_result = analyze_with_fallback_text(user_prompt, "Изображение еды")
        
        if "error" in langdock_result:
            return langdock_result
        
        # Use AI-only analysis (OpenCV disabled for Vercel compatibility)
        result = langdock_result.copy()
        
        # Ensure all required fields are present
        if "food_items" not in result:
            result["food_items"] = []
        
        if "reference_object" not in result:
            result["reference_object"] = {
                "type": "unknown",
                "name": "Эталонный объект не найден",
                "confidence": 0.0
            }
        
        if "estimated_weight" not in result:
            total_weight = sum(item.get("estimated_weight", 0) for item in result["food_items"])
            result["estimated_weight"] = total_weight
        
        if "confidence" not in result:
            if result["food_items"]:
                avg_confidence = sum(item.get("confidence", 0) for item in result["food_items"]) / len(result["food_items"])
                result["confidence"] = avg_confidence
            else:
                result["confidence"] = 0.0
        
        # Add note about simplified analysis
        result["analysis_mode"] = "ai_only"
        result["note"] = "Анализ выполнен только с помощью ИИ (OpenCV отключен для совместимости с Vercel)"
        
        return result
        
    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        return {"error": f"Image processing failed: {str(e)}"}


def handler(request):
    """Vercel function handler"""
    try:
        # Parse request
        if request.method != "POST":
            return {
                "statusCode": 405,
                "body": json.dumps({"error": "Method not allowed"})
            }
        
        # Get request data
        try:
            if hasattr(request, 'get_json'):
                data = request.get_json()
            else:
                import json
                data = json.loads(request.body)
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Invalid JSON: {str(e)}"})
            }
        
        # Validate required fields
        if not data or "image" not in data:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing image data"})
            }
        
        image_base64 = data["image"]
        user_prompt = data.get("user_prompt", "Analyze this food photo and estimate portion size")
        
        # Process image
        result = process_image(image_base64, user_prompt)
        
        # Return result
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }


# For local testing
if __name__ == "__main__":
    # Test with a sample request
    test_request = type('Request', (), {
        'method': 'POST',
        'body': json.dumps({
            "image": "base64_image_data_here",
            "user_prompt": "Analyze this food photo"
        })
    })()
    
    result = handler(test_request)
    print(json.dumps(result, indent=2))
