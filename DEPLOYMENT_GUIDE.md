# 🚀 Полное руководство по развертыванию Nutrition Bot

## Архитектура развертывания

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Railway.app   │    │ Neon PostgreSQL │    │     Vercel      │
│  (Main Bot)     │◄──►│   (Database)    │    │ (Image Processing)│
│   24/7 работа   │    │   3GB бесплатно │    │  Serverless API │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                                              ▲
         │                                              │
         └──────────────── HTTP API ────────────────────┘
                                │
                    ┌─────────────────┐
                    │  UptimeRobot    │
                    │  (Monitoring)   │
                    │  Health Checks  │
                    └─────────────────┘
```

## 📋 Пошаговое развертывание

### 1️⃣ Подготовка Telegram Bot

1. **Создайте бота через @BotFather:**
   ```
   /newbot
   Название: Nutrition Bot
   Username: your_nutrition_bot
   ```

2. **Получите токен бота** и сохраните его

3. **Настройте команды бота:**
   ```
   /setcommands
   start - Запуск бота и регистрация
   help - Справка по командам
   stats - Статистика питания
   goal - Установить дневную цель
   history - История записей
   clear - Очистить данные за день
   lang - Изменить язык
   ```

### 2️⃣ Настройка базы данных Neon PostgreSQL

1. **Регистрация на Neon.tech:**
   - Перейдите на https://neon.tech
   - Зарегистрируйтесь через GitHub
   - Создайте новый проект "nutrition-bot"

2. **Получите строку подключения:**
   ```
   postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```

3. **Создайте таблицы** (автоматически при первом запуске бота)

### 3️⃣ Развертывание Vercel Functions

1. **Установите Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Войдите в аккаунт:**
   ```bash
   vercel login
   ```

3. **Разверните функции:**
   ```bash
   cd vercel
   vercel --prod
   ```

4. **Настройте переменные окружения в Vercel:**
   ```bash
   vercel env add OPENAI_API_KEY
   vercel env add OPENFOODFACTS_API_URL
   ```

5. **Получите URL вашего Vercel проекта:**
   ```
   https://your-project.vercel.app
   ```

### 4️⃣ Развертывание основного бота на Railway

1. **Подготовьте репозиторий:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/nutrition-bot.git
   git push -u origin main
   ```

2. **Регистрация на Railway.app:**
   - Перейдите на https://railway.app
   - Войдите через GitHub
   - Нажмите "New Project" → "Deploy from GitHub repo"

3. **Выберите ваш репозиторий** и подтвердите развертывание

4. **Настройте переменные окружения в Railway:**
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   NEON_DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   VERCEL_API_URL=https://your-project.vercel.app
   OPENAI_API_KEY=your_openai_key_here
   RAILWAY_ENVIRONMENT=production
   PORT=8000
   ```

5. **Получите URL вашего Railway приложения:**
   ```
   https://your-app.up.railway.app
   ```

### 5️⃣ Настройка мониторинга UptimeRobot

1. **Регистрация на UptimeRobot.com:**
   - Создайте бесплатный аккаунт
   - Перейдите в Dashboard

2. **Создайте HTTP Monitor:**
   - URL: `https://your-app.up.railway.app/health`
   - Monitoring Interval: 5 minutes
   - Monitor Type: HTTP(s)

3. **Настройте уведомления:**
   - Email alerts при недоступности > 2 минут
   - Telegram уведомления (опционально)

## 🔧 Конфигурационные файлы

### .env файл для локальной разработки
```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Database
NEON_DATABASE_URL=postgresql://username:password@localhost:5432/nutrition_bot

# External APIs
OPENAI_API_KEY=your_openai_key_here
VERCEL_API_URL=https://your-project.vercel.app

# Environment
RAILWAY_ENVIRONMENT=development
PORT=8000
LOG_LEVEL=INFO

# Optional
REDIS_URL=redis://localhost:6379
SENTRY_DSN=your_sentry_dsn_here
```

### railway.toml
```toml
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"

[[services]]
name = "nutrition-bot"
```

### vercel.json
```json
{
  "functions": {
    "api/analyze-photo.py": {
      "runtime": "python3.9",
      "maxDuration": 30
    },
    "api/process-barcode.py": {
      "runtime": "python3.9", 
      "maxDuration": 15
    },
    "api/health.py": {
      "runtime": "python3.9",
      "maxDuration": 10
    }
  },
  "env": {
    "OPENAI_API_KEY": "@openai_api_key",
    "OPENFOODFACTS_API_URL": "https://world.openfoodfacts.org/api"
  }
}
```

## 🚀 Команды для запуска

### Локальная разработка
```bash
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Настройте .env файл
cp .env.example .env
# Отредактируйте .env с вашими данными

# 3. Запустите локальную PostgreSQL (или используйте Neon)
docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres

# 4. Запустите бота
python main.py
```

### Тестирование Vercel функций локально
```bash
cd vercel
vercel dev
```

### Развертывание обновлений

**Railway (автоматически при push в main):**
```bash
git add .
git commit -m "Update bot"
git push origin main
```

**Vercel:**
```bash
cd vercel
vercel --prod
```

## 📊 Мониторинг и логи

### Просмотр логов Railway
```bash
# Установите Railway CLI
npm install -g @railway/cli

# Войдите в аккаунт
railway login

# Просмотрите логи
railway logs
```

### Health Check endpoints

**Railway Bot:**
- `GET https://your-app.up.railway.app/health`
- Возвращает статус бота и базы данных

**Vercel Functions:**
- `GET https://your-project.vercel.app/api/health`
- Возвращает статус serverless функций

### Пример ответа health check:
```json
{
  "status": "healthy",
  "database": "connected",
  "bot": "connected",
  "bot_username": "your_nutrition_bot",
  "timestamp": 1703123456.789
}
```

## 🔒 Безопасность

### Переменные окружения
- ✅ Все API ключи в переменных окружения
- ✅ Никогда не коммитьте .env файлы
- ✅ Используйте разные ключи для dev/prod

### Rate Limiting
- ✅ Встроенная защита от спама
- ✅ Лимиты на количество запросов
- ✅ Валидация размеров изображений

## 🐛 Отладка и решение проблем

### Частые проблемы:

**1. Бот не отвечает:**
```bash
# Проверьте логи Railway
railway logs

# Проверьте health check
curl https://your-app.up.railway.app/health
```

**2. Ошибки базы данных:**
```bash
# Проверьте строку подключения Neon
# Убедитесь что IP не заблокирован
```

**3. Vercel функции не работают:**
```bash
# Проверьте логи Vercel
vercel logs

# Тестируйте локально
vercel dev
```

**4. Проблемы с изображениями:**
```bash
# Проверьте размер изображения (макс 20MB)
# Убедитесь что OpenAI API ключ валиден
```

## 💰 Лимиты бесплатных тарифов

### Railway.app
- ✅ $5 кредитов в месяц
- ✅ 24/7 работа без засыпания
- ✅ 1GB RAM, 1 vCPU

### Neon PostgreSQL
- ✅ 3GB хранилища
- ✅ Неограниченное время работы
- ✅ 1 база данных

### Vercel
- ✅ 100GB bandwidth
- ✅ 100 serverless функций
- ✅ Неограниченные запросы

### OpenAI API
- 💰 Платный (примерно $0.01 за анализ изображения)
- 💡 Альтернатива: используйте локальные модели

## 🔄 Автоматическое развертывание

### GitHub Actions (опционально)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to Railway
      uses: railway-app/railway-action@v1
      with:
        railway-token: ${{ secrets.RAILWAY_TOKEN }}
```

## 📈 Масштабирование

### При росте пользователей:
1. **Railway Pro** ($20/месяц) - больше ресурсов
2. **Neon Pro** ($19/месяц) - больше хранилища
3. **Vercel Pro** ($20/месяц) - больше функций
4. **Redis** для кэширования
5. **Sentry** для мониторинга ошибок

## ✅ Чек-лист развертывания

- [ ] Создан Telegram бот через @BotFather
- [ ] Настроена база данных Neon PostgreSQL
- [ ] Развернуты Vercel функции
- [ ] Настроен Railway с переменными окружения
- [ ] Добавлен мониторинг UptimeRobot
- [ ] Проверены health check endpoints
- [ ] Протестированы все функции бота
- [ ] Настроены уведомления об ошибках

Теперь ваш Nutrition Bot готов к работе в production среде! 🎉
