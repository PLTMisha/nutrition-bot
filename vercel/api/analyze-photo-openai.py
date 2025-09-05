"""
Vercel function for analyzing food photos using GPT-4 Vision and OpenCV
"""
import json
import base64
import os
import logging
from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image
import openai
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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


def analyze_with_gpt4_vision(image_base64: str, user_prompt: str) -> Dict[str, Any]:
    """Analyze image using GPT-4 Vision"""
    try:
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
        
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
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
            max_tokens=1000,
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        
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
                
    except Exception as e:
        logger.error(f"GPT-4 Vision analysis failed: {e}")
        return {"error": f"AI analysis failed: {str(e)}"}


def detect_reference_object_opencv(image: np.ndarray) -> Optional[Dict[str, Any]]:
    """Detect reference objects using OpenCV"""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect circles (coins, plates, cups)
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=30,
            param1=50,
            param2=30,
            minRadius=10,
            maxRadius=200
        )
        
        detected_objects = []
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                diameter_pixels = r * 2
                
                # Try to match with known circular objects
                for obj_key, obj_data in REFERENCE_OBJECTS.items():
                    if "diameter" in obj_data:
                        expected_diameter = obj_data["diameter"]
                        # Calculate scale factor
                        scale_factor = expected_diameter / diameter_pixels
                        
                        detected_objects.append({
                            "type": obj_key,
                            "name": obj_data["name"],
                            "pixel_size": diameter_pixels,
                            "real_size": expected_diameter,
                            "scale_factor": scale_factor,
                            "confidence": 0.7,  # OpenCV detection confidence
                            "position": (int(x), int(y))
                        })
        
        # Detect rectangles (cards, matchboxes, phones)
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if it's roughly rectangular (4 corners)
            if len(approx) == 4:
                rect = cv2.boundingRect(contour)
                width, height = rect[2], rect[3]
                
                # Skip very small rectangles
                if width < 20 or height < 20:
                    continue
                
                aspect_ratio = max(width, height) / min(width, height)
                
                # Credit card aspect ratio is approximately 1.6
                if 1.4 <= aspect_ratio <= 1.8:
                    # Likely a credit card
                    card_data = REFERENCE_OBJECTS["credit_card"]
                    scale_factor = card_data["length"] / max(width, height)
                    
                    detected_objects.append({
                        "type": "credit_card",
                        "name": card_data["name"],
                        "pixel_size": max(width, height),
                        "real_size": card_data["length"],
                        "scale_factor": scale_factor,
                        "confidence": 0.6,
                        "position": (rect[0] + width//2, rect[1] + height//2)
                    })
        
        # Return the most confident detection
        if detected_objects:
            best_object = max(detected_objects, key=lambda x: x["confidence"])
            return best_object
        
        return None
        
    except Exception as e:
        logger.error(f"OpenCV detection failed: {e}")
        return None


def calculate_food_weight(
    food_area_pixels: int,
    reference_object: Dict[str, Any],
    food_type: str = "general"
) -> float:
    """Calculate food weight based on area and reference object"""
    try:
        scale_factor = reference_object.get("scale_factor", 1.0)
        
        # Convert pixel area to real area (mm²)
        real_area_mm2 = food_area_pixels * (scale_factor ** 2)
        
        # Convert to cm²
        real_area_cm2 = real_area_mm2 / 100
        
        # Estimate weight based on food type and area
        # These are rough estimates for different food densities
        density_factors = {
            "rice": 0.8,      # g/cm²
            "pasta": 0.7,
            "meat": 1.2,
            "vegetables": 0.5,
            "bread": 0.6,
            "soup": 1.0,
            "salad": 0.3,
            "general": 0.8    # default
        }
        
        density = density_factors.get(food_type.lower(), density_factors["general"])
        estimated_weight = real_area_cm2 * density
        
        return max(10, min(2000, estimated_weight))  # Clamp between 10g and 2kg
        
    except Exception as e:
        logger.error(f"Weight calculation failed: {e}")
        return 100  # Default weight


def process_image(image_base64: str, user_prompt: str) -> Dict[str, Any]:
    """Main image processing function"""
    try:
        # Decode base64 image
        image_data = base64.b64decode(image_base64)
        image_pil = Image.open(BytesIO(image_data))
        
        # Convert to OpenCV format
        image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        
        # Analyze with GPT-4 Vision
        gpt_result = analyze_with_gpt4_vision(image_base64, user_prompt)
        
        if "error" in gpt_result:
            return gpt_result
        
        # Enhance with OpenCV detection
        opencv_reference = detect_reference_object_opencv(image_cv)
        
        # Combine results
        result = gpt_result.copy()
        
        # If OpenCV found a reference object, use it to refine the analysis
        if opencv_reference and "reference_object" in result:
            # Update reference object with OpenCV data
            result["reference_object"].update({
                "opencv_detection": True,
                "pixel_size": opencv_reference["pixel_size"],
                "scale_factor": opencv_reference["scale_factor"]
            })
            
            # Recalculate food weights if needed
            if "food_items" in result:
                for item in result["food_items"]:
                    # Use OpenCV scale factor for more accurate weight estimation
                    if "estimated_weight" in item:
                        # Adjust weight based on OpenCV scale factor
                        adjustment_factor = opencv_reference["scale_factor"] / result.get("scale_factor", 1.0)
                        item["estimated_weight"] = item["estimated_weight"] * adjustment_factor
        
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
