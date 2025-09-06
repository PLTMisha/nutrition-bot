# Финальная Настройка Переменных Railway

## Исправленные Проблемы
✅ Переменные окружения теперь работают (прямой доступ к os.environ)
✅ Исправлен импорт List в services/vercel_api.py

## Установите Эти Переменные в Railway

### Через Railway Dashboard:
1. Откройте ваш проект в Railway
2. Перейдите в Variables
3. Добавьте следующие переменные:

```
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
NEON_DATABASE_URL=ваш_postgresql_url_от_neon
VERCEL_API_URL=https://nutrition-lsm0p4sko-michaels-projects-52325f35.vercel.app
LANGDOCK_API_KEY=ваш_ключ_от_langdock
```

### Через Railway CLI:
```bash
railway variables set TELEGRAM_BOT_TOKEN="ваш_токен_от_BotFather"
railway variables set NEON_DATABASE_URL="ваш_postgresql_url_от_neon"  
railway variables set VERCEL_API_URL="https://nutrition-lsm0p4sko-michaels-projects-52325f35.vercel.app"
railway variables set LANGDOCK_API_KEY="ваш_ключ_от_langdock"
```

## Где Получить Значения:

### 1. TELEGRAM_BOT_TOKEN
- Напишите @BotFather в Telegram
- Создайте нового бота командой `/newbot`
- Скопируйте токен (формат: `123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 2. NEON_DATABASE_URL
- Зайдите в https://neon.tech
- Создайте новую базу данных
- Скопируйте Connection String (формат: `postgresql://user:pass@host/dbname`)

### 3. VERCEL_API_URL
✅ Уже готов: `https://nutrition-lsm0p4sko-michaels-projects-52325f35.vercel.app`

### 4. LANGDOCK_API_KEY
- Зайдите в https://langdock.com
- Получите API ключ (формат: `sk-...`)

## Ожидаемый Результат

После установки переменных и развертывания вы должны увидеть в логах:

```
=== ENVIRONMENT VARIABLES DEBUG ===
RAILWAY_ENVIRONMENT=production
PORT=8080
TELEGRAM_BOT_TOKEN=123456789:ABC...
NEON_DATABASE_URL=postgresql://...
VERCEL_API_URL=https://nutrition-lsm0p4sko-michaels-projects-52325f35.vercel.app
LANGDOCK_API_KEY=sk-...
=== END DEBUG ===

Starting Telegram bot...
Bot started successfully!
Health check endpoint available at /health
```

## Проверка Работы

1. **Telegram Bot**: Найдите вашего бота в Telegram и отправьте `/start`
2. **Health Check**: Откройте `https://ваш-railway-url.up.railway.app/health`
3. **Vercel Functions**: Проверьте что Vercel функции отвечают

Бот готов к использованию! 🎉
