# 🚀 Полное руководство по развертыванию Nutrition Bot
## Render.com + Vercel + Neon + Langdock

### 📋 Архитектура приложения

Ваш проект состоит из:
- **Telegram Bot** (основное приложение) → **Render.com**
- **API функции** для обработки изображений → **Vercel**
- **База данных** PostgreSQL → **Neon**
- **ИИ сервис** для анализа → **Langdock**

---

## 🗄️ Шаг 1: Настройка базы данных Neon

### 1.1 Создание проекта в Neon
1. Перейдите на [neon.tech](https://neon.tech)
2. Зарегистрируйтесь/войдите в аккаунт
3. Создайте новый проект: **"nutrition-bot-db"**
4. Выберите регион (рекомендуется ближайший к вам)
5. Скопируйте строку подключения к БД

### 1.2 Получение строки подключения
```
postgresql://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
```

---

## ⚡ Шаг 2: Настройка Vercel для API функций

### 2.1 Подготовка проекта для Vercel
1. Создайте новый репозиторий на GitHub
2. Загрузите только папку `vercel/` в корень репозитория

### 2.2 Создание Langdock API функции
Создайте файл `vercel/api/analyze-photo-langdock.py`:

```python
import os
import json
import base64
import requests
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Получаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Получаем изображение
            image_data = data.get('image')
            if not image_data:
                self.send_error(400, "No image data provided")
                return
            
            # Настройки Langdock
            api_key = os.environ.get('LANGDOCK_API_KEY')
            if not api_key:
                self.send_error(500, "Langdock API key not configured")
                return
            
            # Подготавливаем запрос к Langdock
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Проанализируй это изображение еды и предоставь информацию о питательной ценности, калориях и ингредиентах на русском языке."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            # Отправляем запрос к Langdock
            response = requests.post(
                'https://api.langdock.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result['choices'][0]['message']['content']
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response_data = {
                    'success': True,
                    'analysis': analysis
                }
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_error(500, f"Langdock API error: {response.status_code}")
                
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_data = {
            'service': 'Langdock Photo Analysis API',
            'status': 'running'
        }
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
```

### 2.3 Развертывание на Vercel
1. Перейдите на [vercel.com](https://vercel.com)
2. Подключите GitHub репозиторий
3. Настройте переменные окружения:
   - `LANGDOCK_API_KEY` = ваш API ключ Langdock
4. Деплой произойдет автоматически
5. Скопируйте URL вашего Vercel приложения

---

## 🖥️ Шаг 3: Настройка Render.com для основного бота

### 3.1 Подготовка кода для Render
Создайте файл `render.yaml` в корне проекта:

```yaml
services:
  - type: web
    name: nutrition-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.18
      - key: PORT
        fromService:
          type: web
          name: nutrition-bot
          property: port
```

### 3.2 Обновление requirements.txt для Render
```txt
# Telegram Bot Framework
aiogram==3.4.1

# Database
asyncpg==0.29.0
SQLAlchemy==2.0.25
alembic==1.13.1

# HTTP Client
aiohttp==3.9.1

# Environment Variables
python-dotenv==1.0.0

# Image Processing
Pillow==10.1.0

# Data Processing
pandas==2.1.4

# Validation
pydantic==2.5.2
pydantic-settings==2.1.0

# Logging
structlog==23.2.0

# Utilities
python-dateutil==2.8.2
pytz==2023.3

# For Render deployment
gunicorn==21.2.0
```

### 3.3 Создание Dockerfile для Render (опционально)
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE $PORT

CMD ["python", "main.py"]
```

### 3.4 Развертывание на Render
1. Перейдите на [render.com](https://render.com)
2. Создайте новый **Web Service**
3. Подключите ваш GitHub репозиторий
4. Настройте:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

---

## 🔧 Шаг 4: Настройка переменных окружения

### 4.1 Переменные для Render.com
```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Database (Neon)
NEON_DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# Vercel API
VERCEL_API_URL=https://your-vercel-app.vercel.app
VERCEL_API_KEY=optional_if_needed

# Langdock API
LANGDOCK_API_KEY=your_langdock_api_key

# Render specific
PORT=10000
FORCE_WEBHOOK_MODE=true
RAILWAY_ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_REQUESTS=30
RATE_LIMIT_WINDOW=60

# Cache Settings
CACHE_TTL=3600
MAX_CACHE_SIZE=1000

# Image Processing
MAX_IMAGE_SIZE=10485760
ALLOWED_IMAGE_TYPES=jpg,jpeg,png,webp

# Open Food Facts
OPENFOODFACTS_API_URL=https://world.openfoodfacts.org/api
```

### 4.2 Переменные для Vercel
```env
LANGDOCK_API_KEY=your_langdock_api_key
```

---

## 🔄 Шаг 5: Обновление кода для новой архитектуры

### 5.1 Обновление config/settings.py
Добавьте поддержку Langdock вместо OpenAI:

```python
# Langdock configuration (replaces OpenAI)
LANGDOCK_CONFIG = {
    "api_key": settings.langdock_api_key,
    "base_url": "https://api.langdock.com/v1",
    "model": "gpt-4-vision-preview",
    "max_tokens": 1000,
    "temperature": 0.1,
}
```

### 5.2 Обновление .env.example
```env
# Langdock Configuration (replaces OpenAI)
LANGDOCK_API_KEY=your_langdock_api_key

# Remove OpenAI
# OPENAI_API_KEY=your_openai_api_key
```

---

## 🚀 Шаг 6: Пошаговое развертывание

### 6.1 Порядок развертывания
1. **Neon Database** (создать БД и получить URL)
2. **Vercel API** (развернуть API функции)
3. **Render Bot** (развернуть основное приложение)
4. **Настройка Webhook** (настроить Telegram webhook)

### 6.2 Команды для локального тестирования
```bash
# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
cp .env.example .env
# Заполните переменные окружения

# Запуск в режиме polling (для тестирования)
export FORCE_POLLING_MODE=true
python main.py

# Запуск в режиме webhook (для продакшена)
export FORCE_WEBHOOK_MODE=true
python main.py
```

---

## 🔍 Шаг 7: Тестирование и отладка

### 7.1 Проверка здоровья сервисов
- **Render**: `https://your-render-app.onrender.com/health`
- **Vercel**: `https://your-vercel-app.vercel.app/api/health`
- **Database**: проверяется автоматически через health endpoint

### 7.2 Логи и мониторинг
- **Render**: встроенные логи в панели управления
- **Vercel**: логи функций в панели управления
- **Neon**: мониторинг БД в панели управления

### 7.3 Типичные проблемы и решения

**Проблема**: Бот не отвечает
**Решение**: Проверьте webhook URL и переменные окружения

**Проблема**: Ошибки базы данных
**Решение**: Проверьте строку подключения Neon и доступность БД

**Проблема**: API функции не работают
**Решение**: Проверьте Langdock API ключ и лимиты

---

## 💰 Стоимость использования (бесплатные лимиты)

- **Render.com**: 750 часов/месяц бесплатно
- **Vercel**: 100GB bandwidth + 100GB-Hrs бесплатно
- **Neon**: 0.5GB storage + 100 часов compute бесплатно
- **Langdock**: зависит от вашего плана

---

## 📞 Поддержка и помощь

Если возникнут проблемы:
1. Проверьте логи в панелях управления сервисов
2. Убедитесь, что все переменные окружения настроены правильно
3. Проверьте health endpoints всех сервисов
4. Используйте режим polling для локальной отладки

**Готово!** Ваш бот должен работать на новой архитектуре.
