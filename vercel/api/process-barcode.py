"""
Vercel function for processing barcode images using pyzbar
"""
import json
import base64
import os
import logging
from io import BytesIO
from typing import Dict, Any, List, Optional

import cv2
import numpy as np
from PIL import Image
from pyzbar import pyzbar
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Open Food Facts API configuration
OPENFOODFACTS_API_URL = os.environ.get("OPENFOODFACTS_API_URL", "https://world.openfoodfacts.org/api")


def preprocess_image_for_barcode(image: np.ndarray) -> List[np.ndarray]:
    """Preprocess image to improve barcode detection"""
    processed_images = []
    
    # Original image
    processed_images.append(image)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed_images.append(gray)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    processed_images.append(blurred)
    
    # Apply threshold to create binary image
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    processed_images.append(thresh)
    
    # Apply adaptive threshold
    adaptive_thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    processed_images.append(adaptive_thresh)
    
    # Apply morphological operations to clean up the image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    processed_images.append(morph)
    
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    processed_images.append(enhanced)
    
    return processed_images


def detect_barcode(image_data: bytes) -> Optional[Dict[str, Any]]:
    """Detect barcode from image data"""
    try:
        # Convert bytes to PIL Image
        image_pil = Image.open(BytesIO(image_data))
        
        # Convert to OpenCV format
        image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        
        # Preprocess image for better barcode detection
        processed_images = preprocess_image_for_barcode(image_cv)
        
        detected_barcodes = []
        
        # Try to detect barcodes in each processed image
        for i, processed_img in enumerate(processed_images):
            try:
                # Detect barcodes using pyzbar
                barcodes = pyzbar.decode(processed_img)
                
                for barcode in barcodes:
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    
                    # Get barcode position
                    rect = barcode.rect
                    
                    detected_barcodes.append({
                        "data": barcode_data,
                        "type": barcode_type,
                        "position": {
                            "x": rect.left,
                            "y": rect.top,
                            "width": rect.width,
                            "height": rect.height
                        },
                        "preprocessing_method": i,
                        "confidence": 1.0  # pyzbar doesn't provide confidence, so we use 1.0
                    })
                    
            except Exception as e:
                logger.warning(f"Error processing image variant {i}: {e}")
                continue
        
        if not detected_barcodes:
            return None
        
        # Return the first detected barcode (usually the most reliable)
        best_barcode = detected_barcodes[0]
        
        # Validate barcode format
        barcode_data = best_barcode["data"]
        if not barcode_data.isdigit() or len(barcode_data) < 8:
            logger.warning(f"Invalid barcode format: {barcode_data}")
            return None
        
        return {
            "barcode": barcode_data,
            "type": best_barcode["type"],
            "position": best_barcode["position"],
            "confidence": best_barcode["confidence"]
        }
        
    except Exception as e:
        logger.error(f"Barcode detection failed: {e}")
        return None


def get_product_info_from_openfoodfacts(barcode: str) -> Optional[Dict[str, Any]]:
    """Get product information from Open Food Facts API"""
    try:
        url = f"{OPENFOODFACTS_API_URL}/v2/product/{barcode}.json"
        
        headers = {
            "User-Agent": "NutritionBot/1.0 (Vercel Function)"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"OpenFoodFacts API returned status {response.status_code}")
            return None
        
        data = response.json()
        
        if data.get("status") != 1:
            logger.info(f"Product not found in OpenFoodFacts: {barcode}")
            return None
        
        product = data.get("product", {})
        
        # Extract product information
        name = product.get("product_name") or product.get("product_name_en")
        if not name:
            name = product.get("generic_name") or "Unknown Product"
        
        brand = product.get("brands", "").split(",")[0].strip() if product.get("brands") else None
        
        # Extract nutrition information (per 100g)
        nutriments = product.get("nutriments", {})
        
        def get_nutrition_value(keys, conversion_factor=1.0):
            for key in keys:
                value = nutriments.get(key)
                if value is not None:
                    try:
                        return float(value) * conversion_factor
                    except (ValueError, TypeError):
                        continue
            return None
        
        calories = get_nutrition_value(["energy-kcal_100g", "energy_100g"], 0.239006)  # kJ to kcal
        proteins = get_nutrition_value(["proteins_100g"])
        fats = get_nutrition_value(["fat_100g"])
        carbs = get_nutrition_value(["carbohydrates_100g"])
        
        # Additional nutrition info
        fiber = get_nutrition_value(["fiber_100g"])
        sugar = get_nutrition_value(["sugars_100g"])
        sodium = get_nutrition_value(["sodium_100g"])
        
        # Set defaults for missing values
        calories = calories or 0
        proteins = proteins or 0
        fats = fats or 0
        carbs = carbs or 0
        
        # Additional metadata
        categories = product.get("categories", "")
        image_url = product.get("image_url") or product.get("image_front_url")
        
        return {
            "name": name.strip(),
            "brand": brand,
            "barcode": barcode,
            "calories_per_100g": float(calories),
            "proteins_per_100g": float(proteins),
            "fats_per_100g": float(fats),
            "carbs_per_100g": float(carbs),
            "fiber_per_100g": float(fiber) if fiber is not None else None,
            "sugar_per_100g": float(sugar) if sugar is not None else None,
            "sodium_per_100g": float(sodium) if sodium is not None else None,
            "category": categories.split(",")[0].strip() if categories else None,
            "image_url": image_url,
            "source": "openfoodfacts"
        }
        
    except requests.RequestException as e:
        logger.error(f"Error fetching product info from OpenFoodFacts: {e}")
        return None
    except Exception as e:
        logger.error(f"Error processing OpenFoodFacts response: {e}")
        return None


def process_barcode_image(image_base64: str) -> Dict[str, Any]:
    """Main barcode processing function"""
    try:
        # Decode base64 image
        image_data = base64.b64decode(image_base64)
        
        # Detect barcode
        barcode_result = detect_barcode(image_data)
        
        if not barcode_result:
            return {"error": "No barcode found in image"}
        
        barcode = barcode_result["barcode"]
        
        # Get product information from Open Food Facts
        product_info = get_product_info_from_openfoodfacts(barcode)
        
        result = {
            "barcode": barcode,
            "barcode_type": barcode_result["type"],
            "detection_confidence": barcode_result["confidence"],
            "position": barcode_result["position"]
        }
        
        if product_info:
            result["product"] = product_info
            result["found_in_database"] = True
        else:
            result["found_in_database"] = False
            result["message"] = "Barcode detected but product not found in database"
        
        return result
        
    except Exception as e:
        logger.error(f"Barcode processing failed: {e}")
        return {"error": f"Barcode processing failed: {str(e)}"}


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
        
        # Process barcode
        result = process_barcode_image(image_base64)
        
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
            "image": "base64_image_data_here"
        })
    })()
    
    result = handler(test_request)
    print(json.dumps(result, indent=2))
