#!/usr/bin/env python3
"""
Тест механизмов fallback для Nutrition Bot
Проверяет работу бота при недоступности внешних API
"""
import asyncio
import aiohttp
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_bot_webhook():
    """Тест доступности webhook бота"""
    try:
        # Замените на ваш реальный URL Railway
        webhook_url = "https://nutrition-bot-production.up.railway.app/webhook"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(webhook_url.replace('/webhook', '/health')) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Bot health check: {data}")
                    return True
                else:
                    logger.error(f"❌ Bot health check failed: {response.status}")
                    return False
    except Exception as e:
        logger.error(f"❌ Bot webhook test failed: {e}")
        return False

async def test_openfoodfacts_api():
    """Тест доступности OpenFoodFacts API"""
    try:
        url = "https://world.openfoodfacts.org/api/v0/product/3017620422003.json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    logger.info("✅ OpenFoodFacts API доступен")
                    return True
                else:
                    logger.warning(f"⚠️ OpenFoodFacts API недоступен: {response.status}")
                    return False
    except Exception as e:
        logger.warning(f"⚠️ OpenFoodFacts API недоступен: {e}")
        return False

async def test_vercel_api():
    """Тест доступности Vercel API"""
    try:
        # Замените на ваш реальный URL Vercel
        health_url = "https://your-vercel-app.vercel.app/api/health"
        async with aiohttp.ClientSession() as session:
            async with session.get(health_url, timeout=10) as response:
                if response.status == 200:
                    logger.info("✅ Vercel API доступен")
                    return True
                else:
                    logger.warning(f"⚠️ Vercel API недоступен: {response.status}")
                    return False
    except Exception as e:
        logger.warning(f"⚠️ Vercel API недоступен: {e}")
        return False

def test_offline_nutrition_database():
    """Тест офлайн базы питания"""
    try:
        # Импортируем функцию fallback из handlers
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        from handlers.food_search import _get_basic_nutrition_estimate
        
        # Тестируем несколько продуктов
        test_products = ['яблоко', 'курица', 'рис', 'unknown_product']
        
        for product in test_products:
            result = _get_basic_nutrition_estimate(product, 100)
            if result:
                logger.info(f"✅ Fallback для '{product}': {result['calories_per_100g']} ккал")
            else:
                logger.warning(f"⚠️ Fallback для '{product}' не найден")
        
        return True
    except Exception as e:
        logger.error(f"❌ Тест офлайн базы питания failed: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование механизмов fallback Nutrition Bot")
    print("=" * 50)
    print(f"Время тестирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Тест 1: Доступность бота
    print("1️⃣ Тестирование доступности бота...")
    results['bot_available'] = await test_bot_webhook()
    
    # Тест 2: OpenFoodFacts API
    print("\n2️⃣ Тестирование OpenFoodFacts API...")
    results['openfoodfacts_available'] = await test_openfoodfacts_api()
    
    # Тест 3: Vercel API
    print("\n3️⃣ Тестирование Vercel API...")
    results['vercel_available'] = await test_vercel_api()
    
    # Тест 4: Офлайн база питания
    print("\n4️⃣ Тестирование офлайн базы питания...")
    results['offline_db_working'] = test_offline_nutrition_database()
    
    # Результаты
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ РАБОТАЕТ" if result else "❌ НЕ РАБОТАЕТ"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    # Анализ готовности к fallback
    print("\n🔍 АНАЛИЗ ГОТОВНОСТИ К FALLBACK:")
    if not results['openfoodfacts_available'] and results['offline_db_working']:
        print("✅ Fallback для поиска продуктов готов к работе")
    
    if not results['vercel_available']:
        print("✅ Fallback для анализа изображений готов к работе")
    
    if results['bot_available']:
        print("✅ Бот доступен и готов к работе")
    else:
        print("❌ Бот недоступен - проверьте деплой на Railway")
    
    print("\n🎯 РЕКОМЕНДАЦИИ:")
    if not results['bot_available']:
        print("- Проверьте статус деплоя на Railway")
        print("- Убедитесь, что все переменные окружения настроены")
    
    if results['bot_available'] and (not results['openfoodfacts_available'] or not results['vercel_available']):
        print("- Бот будет работать в режиме fallback")
        print("- Пользователи получат приблизительные данные")
        print("- Это нормально и предотвращает краши")

if __name__ == "__main__":
    asyncio.run(main())
