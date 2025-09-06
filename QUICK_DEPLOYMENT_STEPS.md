# 🚀 Быстрое развертывание Nutrition Bot
## Render.com + Vercel + Neon + Langdock

### ⚡ Краткий план действий

**Время развертывания: ~30 минут**

---

## 📋 Что вам понадобится

1. **Telegram Bot Token** - получите у [@BotFather](https://t.me/botfather)
2. **Langdock API Key** - ваш токен для ИИ
3. **GitHub аккаунт** - для размещения кода
4. **Аккаунты на платформах**:
   - [Neon.tech](https://neon.tech) (база данных)
   - [Vercel.com](https://vercel.com) (API функции)
   - [Render.com](https://render.com) (основной бот)

---

## 🎯 Пошаговая инструкция

### Шаг 1: Настройка базы данных Neon (5 мин)
1. Зайдите на [neon.tech](https://neon.tech)
2. Создайте проект "nutrition-bot-db"
3. Скопируйте строку подключения:
   ```
   postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```

### Шаг 2: Развертывание API на Vercel (10 мин)
1. Создайте новый репозиторий на GitHub
2. Загрузите папку `vercel/` в корень репозитория
3. Зайдите на [vercel.com](https://vercel.com)
4. Подключите GitHub репозиторий
5. Добавьте переменную окружения:
   - `LANGDOCK_API_KEY` = ваш API ключ
6. Скопируйте URL приложения (например: `https://your-app.vercel.app`)

### Шаг 3: Развертывание бота на Render (10 мин)
1. Загрузите весь проект в GitHub (или создайте новый репозиторий)
2. Зайдите на [render.com](https://render.com)
3. Создайте новый **Web Service**
4. Подключите GitHub репозиторий
5. Настройте:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

### Шаг 4: Настройка переменных окружения в Render (5 мин)
Добавьте следующие переменные:

```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота
NEON_DATABASE_URL=строка_подключения_neon
VERCEL_API_URL=https://your-vercel-app.vercel.app
LANGDOCK_API_KEY=ваш_langdock_ключ
PORT=10000
FORCE_WEBHOOK_MODE=true
RAILWAY_ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Шаг 5: Тестирование (5 мин)
1. Дождитесь успешного деплоя на Render
2. Проверьте health endpoint: `https://your-render-app.onrender.com/health`
3. Напишите боту в Telegram - он должен ответить!

---

## 🔧 Готовые файлы для копирования

### vercel/vercel.json
```json
{
  "functions": {
    "api/*.py": {
      "maxDuration": 30
    }
  }
}
```

### vercel/requirements.txt
```txt
requests==2.31.0
```

### render.yaml (опционально)
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
```

---

## 🚨 Возможные проблемы и решения

### Проблема: Бот не отвечает
**Решение**: 
1. Проверьте логи в Render
2. Убедитесь, что `TELEGRAM_BOT_TOKEN` правильный
3. Проверьте health endpoint

### Проблема: Ошибки базы данных
**Решение**:
1. Проверьте строку подключения Neon
2. Убедитесь, что база данных активна
3. Проверьте лимиты Neon (0.5GB бесплатно)

### Проблема: API функции не работают
**Решение**:
1. Проверьте `LANGDOCK_API_KEY`
2. Убедитесь, что Vercel деплой прошел успешно
3. Проверьте логи функций в Vercel

---

## 💰 Бесплатные лимиты

- **Render**: 750 часов/месяц
- **Vercel**: 100GB трафика
- **Neon**: 0.5GB хранилища + 100 часов compute
- **Langdock**: зависит от вашего плана

---

## 📞 Поддержка

Если что-то не работает:
1. Проверьте все переменные окружения
2. Посмотрите логи в панелях управления
3. Убедитесь, что все сервисы запущены
4. Используйте health endpoints для диагностики

**Готово!** Ваш бот должен работать на новой архитектуре.

---

## 🔗 Полезные ссылки

- [Подробное руководство](./RENDER_VERCEL_NEON_DEPLOYMENT_GUIDE.md)
- [Настройка Telegram бота](https://core.telegram.org/bots#6-botfather)
- [Документация Neon](https://neon.tech/docs)
- [Документация Vercel](https://vercel.com/docs)
- [Документация Render](https://render.com/docs)
