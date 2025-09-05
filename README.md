# Nutrition Bot - Масштабируемый Telegram-бот для подсчета БЖУ

Высокопроизводительный Telegram-бот на Python для подсчета калорий и БЖУ с микросервисной архитектурой.

## 🏗️ Архитектура

- **Railway.app** - основной Telegram-бот (24/7)
- **Neon PostgreSQL** - база данных (3GB)
- **Vercel** - serverless функции для обработки изображений
- **Open Food Facts API** - база данных продуктов
- **GPT-4 Vision** - анализ фотографий блюд
- **OpenCV + pyzbar** - обработка штрих-кодов

## ✨ Функции

### 🔍 Поиск продуктов
- Поиск по названию в базе Open Food Facts
- Кэширование популярных продуктов
- Автодополнение и предложения

### 📱 Сканирование штрих-кодов
- Распознавание штрих-кодов с фотографий
- Интеграция с Open Food Facts API
- Поддержка EAN-8, EAN-13, UPC-A форматов

### 🍽️ Анализ фотографий блюд
- GPT-4 Vision для определения блюд
- OpenCV для измерения пропорций
- Поддержка эталонных объектов (монеты, ложки, тарелки)
- Автоматическая оценка веса порций

### 📊 Статистика и аналитика
- Дневная/недельная/месячная статистика
- Прогресс к целям
- Графики потребления БЖУ
- Экспорт данных в CSV

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.11+
- PostgreSQL (или Neon аккаунт)
- Telegram Bot Token
- OpenAI API Key
- Vercel аккаунт (опционально)

### Локальная установка

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd nutrition-bot
```

2. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

3. **Настройка переменных окружения**
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

4. **Настройка базы данных**
```bash
# Создайте базу данных PostgreSQL
# Обновите NEON_DATABASE_URL в .env
```

5. **Запуск бота**
```bash
python main.py
```

## 🌐 Развертывание в продакшене

### Railway.app (Основной бот)

1. **Создание проекта**
   - Зайдите на [Railway.app](https://railway.app)
   - Создайте новый проект из GitHub репозитория

2. **Настройка переменных окружения**
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   NEON_DATABASE_URL=postgresql://...
   VERCEL_API_URL=https://your-vercel-app.vercel.app
   OPENAI_API_KEY=sk-...
   RAILWAY_ENVIRONMENT=production
   ```

3. **Деплой**
   - Railway автоматически развернет приложение
   - Проверьте логи на наличие ошибок

### Neon PostgreSQL (База данных)

1. **Создание базы данных**
   - Зайдите на [Neon.tech](https://neon.tech)
   - Создайте новую базу данных
   - Скопируйте connection string

2. **Миграции**
   ```bash
   # Таблицы создаются автоматически при первом запуске
   # Или выполните миграции вручную:
   alembic upgrade head
   ```

### Vercel (Функции обработки изображений)

1. **Подготовка**
   ```bash
   cd vercel/
   npm install -g vercel
   ```

2. **Настройка переменных**
   ```bash
   vercel env add OPENAI_API_KEY
   vercel env add OPENFOODFACTS_API_URL
   ```

3. **Деплой**
   ```bash
   vercel --prod
   ```

## 📝 Конфигурация

### Основные настройки (.env)

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Database
NEON_DATABASE_URL=postgresql://username:password@host:port/database

# Vercel API
VERCEL_API_URL=https://your-vercel-app.vercel.app
VERCEL_API_KEY=your_vercel_api_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Настройки производительности
RATE_LIMIT_REQUESTS=30
RATE_LIMIT_WINDOW=60
CACHE_TTL=3600
MAX_CACHE_SIZE=1000
```

### Railway настройки (railway.toml)

```toml
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
```

### Vercel настройки (vercel.json)

```json
{
  "functions": {
    "api/analyze-photo.py": {
      "runtime": "python3.9",
      "maxDuration": 30,
      "memory": 1024
    },
    "api/process-barcode.py": {
      "runtime": "python3.9",
      "maxDuration": 15,
      "memory": 512
    }
  }
}
```

## 🔧 API Endpoints

### Health Check
```
GET /health
```
Возвращает статус здоровья бота и базы данных.

### Vercel Functions

#### Анализ фотографий
```
POST /api/analyze-photo
Content-Type: application/json

{
  "image": "base64_encoded_image",
  "user_prompt": "Analyze this food photo"
}
```

#### Обработка штрих-кодов
```
POST /api/process-barcode
Content-Type: application/json

{
  "image": "base64_encoded_barcode_image"
}
```

## 📊 Мониторинг

### UptimeRobot настройка

1. **HTTP Monitor**
   - URL: `https://your-railway-app.up.railway.app/health`
   - Interval: 5 минут
   - Alert: при недоступности > 2 минут

2. **Keyword Monitor**
   - Keyword: `"status": "healthy"`
   - Alert: если keyword не найден

### Логирование

Логи доступны в:
- Railway: Dashboard → Deployments → Logs
- Vercel: Dashboard → Functions → Logs
- Локально: `nutrition_bot.log`

## 🧪 Тестирование

### Запуск тестов
```bash
pytest tests/ -v
```

### Тестирование API
```bash
# Тест health check
curl https://your-railway-app.up.railway.app/health

# Тест Vercel функций
curl -X POST https://your-vercel-app.vercel.app/api/health
```

## 📈 Масштабирование

### Горизонтальное масштабирование
- Railway: автоматическое масштабирование
- Vercel: serverless автомасштабирование
- Neon: автоматическое масштабирование БД

### Оптимизация производительности
- Кэширование запросов к API
- Пул соединений к БД
- Асинхронная обработка
- Rate limiting

## 🔒 Безопасность

### Переменные окружения
- Никогда не коммитьте `.env` файлы
- Используйте секреты Railway/Vercel
- Регулярно ротируйте API ключи

### Rate Limiting
- 30 запросов в минуту на пользователя
- 5 анализов изображений в минуту
- 10 сканирований штрих-кодов в минуту

### Валидация данных
- Проверка размера изображений (макс 10МБ)
- Санитизация пользовательского ввода
- Валидация форматов файлов

## 🐛 Отладка

### Частые проблемы

1. **База данных недоступна**
   ```bash
   # Проверьте connection string
   psql $NEON_DATABASE_URL
   ```

2. **Vercel функции не работают**
   ```bash
   # Проверьте логи
   vercel logs
   ```

3. **OpenAI API ошибки**
   ```bash
   # Проверьте квоты и ключ
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

### Логи и мониторинг
```bash
# Railway логи
railway logs

# Локальные логи
tail -f nutrition_bot.log

# Проверка статуса
curl https://your-app.up.railway.app/health
```

## 📚 Структура проекта

```
nutrition-bot/
├── main.py                    # Точка входа
├── config/                    # Конфигурация
│   ├── settings.py
│   └── database.py
├── handlers/                  # Telegram handlers
│   ├── basic.py
│   ├── food_search.py
│   ├── media.py
│   └── nutrition.py
├── services/                  # Бизнес-логика
│   ├── database_service.py
│   ├── openfoodfacts.py
│   └── vercel_api.py
├── models/                    # Модели БД
│   └── db_models.py
├── utils/                     # Утилиты
│   ├── cache.py
│   ├── keyboards.py
│   ├── helpers.py
│   └── validators.py
├── vercel/                    # Serverless функции
│   ├── api/
│   │   ├── analyze-photo.py
│   │   ├── process-barcode.py
│   │   └── health.py
│   └── requirements.txt
└── tests/                     # Тесты
```

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Создайте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE).

## 🆘 Поддержка

- 📧 Email: support@nutritionbot.com
- 💬 Telegram: @nutritionbot_support
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)

## 🙏 Благодарности

- [Open Food Facts](https://openfoodfacts.org) - база данных продуктов
- [OpenAI](https://openai.com) - GPT-4 Vision API
- [Railway](https://railway.app) - хостинг приложений
- [Vercel](https://vercel.com) - serverless функции
- [Neon](https://neon.tech) - PostgreSQL база данных
