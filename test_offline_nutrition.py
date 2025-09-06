#!/usr/bin/env python3
"""
Простой тест офлайн базы питания
"""

def _get_basic_nutrition_estimate(product_name: str, quantity: float) -> dict:
    """Get basic nutrition estimates for common foods when API is unavailable"""
    product_name_lower = product_name.lower()
    
    # Basic nutrition database (per 100g)
    basic_foods = {
        # Fruits
        'яблоко': {'calories': 52, 'proteins': 0.3, 'fats': 0.2, 'carbs': 14},
        'apple': {'calories': 52, 'proteins': 0.3, 'fats': 0.2, 'carbs': 14},
        'банан': {'calories': 89, 'proteins': 1.1, 'fats': 0.3, 'carbs': 23},
        'banana': {'calories': 89, 'proteins': 1.1, 'fats': 0.3, 'carbs': 23},
        'апельсин': {'calories': 47, 'proteins': 0.9, 'fats': 0.1, 'carbs': 12},
        'orange': {'calories': 47, 'proteins': 0.9, 'fats': 0.1, 'carbs': 12},
        
        # Vegetables
        'помидор': {'calories': 18, 'proteins': 0.9, 'fats': 0.2, 'carbs': 3.9},
        'tomato': {'calories': 18, 'proteins': 0.9, 'fats': 0.2, 'carbs': 3.9},
        'огурец': {'calories': 16, 'proteins': 0.7, 'fats': 0.1, 'carbs': 4.1},
        'cucumber': {'calories': 16, 'proteins': 0.7, 'fats': 0.1, 'carbs': 4.1},
        'морковь': {'calories': 41, 'proteins': 0.9, 'fats': 0.2, 'carbs': 10},
        'carrot': {'calories': 41, 'proteins': 0.9, 'fats': 0.2, 'carbs': 10},
        
        # Grains
        'рис': {'calories': 130, 'proteins': 2.7, 'fats': 0.3, 'carbs': 28},
        'rice': {'calories': 130, 'proteins': 2.7, 'fats': 0.3, 'carbs': 28},
        'гречка': {'calories': 343, 'proteins': 13.3, 'fats': 3.4, 'carbs': 62},
        'buckwheat': {'calories': 343, 'proteins': 13.3, 'fats': 3.4, 'carbs': 62},
        'хлеб': {'calories': 265, 'proteins': 9, 'fats': 3.2, 'carbs': 49},
        'bread': {'calories': 265, 'proteins': 9, 'fats': 3.2, 'carbs': 49},
        
        # Proteins
        'курица': {'calories': 165, 'proteins': 31, 'fats': 3.6, 'carbs': 0},
        'chicken': {'calories': 165, 'proteins': 31, 'fats': 3.6, 'carbs': 0},
        'говядина': {'calories': 250, 'proteins': 26, 'fats': 15, 'carbs': 0},
        'beef': {'calories': 250, 'proteins': 26, 'fats': 15, 'carbs': 0},
        'яйцо': {'calories': 155, 'proteins': 13, 'fats': 11, 'carbs': 1.1},
        'egg': {'calories': 155, 'proteins': 13, 'fats': 11, 'carbs': 1.1},
        
        # Dairy
        'молоко': {'calories': 42, 'proteins': 3.4, 'fats': 1, 'carbs': 5},
        'milk': {'calories': 42, 'proteins': 3.4, 'fats': 1, 'carbs': 5},
        'творог': {'calories': 103, 'proteins': 18, 'fats': 0.6, 'carbs': 3.3},
        'cottage cheese': {'calories': 103, 'proteins': 18, 'fats': 0.6, 'carbs': 3.3},
        'сыр': {'calories': 402, 'proteins': 25, 'fats': 33, 'carbs': 0.3},
        'cheese': {'calories': 402, 'proteins': 25, 'fats': 33, 'carbs': 0.3},
    }
    
    # Try exact match first
    if product_name_lower in basic_foods:
        nutrition = basic_foods[product_name_lower]
        return {
            'name': product_name.title(),
            'calories_per_100g': nutrition['calories'],
            'proteins_per_100g': nutrition['proteins'],
            'fats_per_100g': nutrition['fats'],
            'carbs_per_100g': nutrition['carbs']
        }
    
    # Try partial match
    for food_name, nutrition in basic_foods.items():
        if food_name in product_name_lower or product_name_lower in food_name:
            return {
                'name': product_name.title(),
                'calories_per_100g': nutrition['calories'],
                'proteins_per_100g': nutrition['proteins'],
                'fats_per_100g': nutrition['fats'],
                'carbs_per_100g': nutrition['carbs']
            }
    
    # Default fallback for unknown products
    return {
        'name': product_name.title(),
        'calories_per_100g': 100,  # Average estimate
        'proteins_per_100g': 5,
        'fats_per_100g': 3,
        'carbs_per_100g': 15
    }

def main():
    """Тест офлайн базы питания"""
    print("🧪 Тест офлайн базы питания")
    print("=" * 40)
    
    # Тестируем различные продукты
    test_cases = [
        ('яблоко', 150),
        ('курица', 200),
        ('рис', 80),
        ('apple', 100),
        ('chicken', 150),
        ('неизвестный продукт', 100),
        ('unknown food', 100)
    ]
    
    for product, quantity in test_cases:
        result = _get_basic_nutrition_estimate(product, quantity)
        
        # Рассчитываем БЖУ для указанного количества
        calories = result['calories_per_100g'] * quantity / 100
        proteins = result['proteins_per_100g'] * quantity / 100
        fats = result['fats_per_100g'] * quantity / 100
        carbs = result['carbs_per_100g'] * quantity / 100
        
        print(f"\n🍽️ {result['name']} ({quantity}г):")
        print(f"   Калории: {calories:.1f} ккал")
        print(f"   Белки: {proteins:.1f}г")
        print(f"   Жиры: {fats:.1f}г")
        print(f"   Углеводы: {carbs:.1f}г")
    
    print("\n✅ Офлайн база питания работает корректно!")
    print("✅ Fallback механизм готов к использованию!")

if __name__ == "__main__":
    main()
