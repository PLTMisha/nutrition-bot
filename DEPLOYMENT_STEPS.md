# 🚀 Пошаговое развертывание Nutrition Bot

## ✅ Готово к развертыванию!

Ваш проект готов к развертыванию в облаке. Следуйте этим шагам:

## 📋 Что вам понадобится:

### 1. Создайте Telegram бота (2 минуты)
1. Откройте Telegram
2. Найдите @BotFather
3. Отправьте `/newbot`
4. Придумайте имя бота (например: "My Nutrition Bot")
5. Придумайте username (например: "my_nutrition_bot")
6. **Сохраните токен** (выглядит как: `1234567890:AAAA-BBB_CCC`)

### 2. Получите Langdock API ключ (2 минуты)
1. Зайдите на https://langdock.com
2. Войдите в аккаунт
3. Перейдите в раздел API Keys или Settings
4. **Скопируйте ваш API ключ**

### 3. Настройте базу данных Neon (3 минуты)
1. Перейдите на https://neon.tech
2. Войдите через GitHub
3. Нажмите "Create project"
4. Назовите проект "nutrition-bot"
5. **Скопируйте connection string** (начинается с `postgresql://`)

## 🚀 Развертывание

### Шаг 1: Разверните основной бот на Railway (5 минут)

1. Зайдите на https://railway.app
2. Войдите через GitHub
3. Нажмите "New Project"
4. Выберите "Deploy from GitHub repo"
5. Найдите и выберите репозиторий `nutrition-bot`
6. Railway автоматически начнет развертывание

**Добавьте переменные окружения:**
1. В проекте Railway перейдите в "Variables"
2. Добавьте следующие переменные:

```
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
NEON_DATABASE_URL=ваша_строка_подключения_neon
LANGDOCK_API_KEY=ваш_langdock_ключ
RAILWAY_ENVIRONMENT=production
PORT=8000
```

3. Нажмите "Deploy" - Railway пересоберет проект с новыми переменными

### Шаг 2: Разверните Vercel функции (3 минуты)

1. Зайдите на https://vercel.com
2. Войдите через GitHub
3. Нажмите "Import Project"
4. Выберите репозиторий `nutrition-bot`
5. **Важно:** В настройках проекта:
   - Root Directory: `vercel`
   - Build Command: оставьте пустым
   - Output Directory: оставьте пустым

**Добавьте переменные окружения в Vercel:**
1. В проекте Vercel перейдите в Settings → Environment Variables
2. Нажмите "Add New" и добавьте каждую переменную отдельно:

**Переменная 1:**
- Name: `LANGDOCK_API_KEY`
- Value: `ваш_langdock_ключ` (без кавычек)
- Environment: Production, Preview, Development (выберите все)

**Переменная 2:**
- Name: `LANGDOCK_BASE_URL`
- Value: `https://api.langdock.com/v1`
- Environment: Production, Preview, Development (выберите все)

**Переменная 3:**
- Name: `OPENFOODFACTS_API_URL`
- Value: `https://world.openfoodfacts.org/api`
- Environment: Production, Preview, Development (выберите все)

3. После добавления всех переменных нажмите "Redeploy" для применения изменений

## ✅ Проверка работы

### 1. Проверьте Railway бота:
1. В Railway откройте ваш проект
2. Перейдите в "Deployments"
3. Убедитесь что статус "Success"
4. Скопируйте URL вашего приложения (например: `https://nutrition-bot-production.up.railway.app`)

### 2. Проверьте Vercel функции:
1. В Vercel откройте ваш проект
2. Перейдите в "Functions"
3. Убедитесь что функции развернуты успешно
4. Скопируйте URL (например: `https://your-project.vercel.app`)

### 3. Обновите URL Vercel в Railway:
1. Вернитесь в Railway
2. В переменных окружения добавьте:
```
VERCEL_API_URL=https://your-project.vercel.app
```

### 4. Настройте webhook Telegram:
1. Откройте в браузере:
```
https://api.telegram.org/bot<ВАШ_ТОКЕН>/setWebhook?url=https://your-railway-app.up.railway.app/webhook
```
2. Замените `<ВАШ_ТОКЕН>` на токен от BotFather
3. Замените `your-railway-app.up.railway.app` на ваш Railway URL
4. Должен вернуться ответ: `{"ok":true,"result":true}`

## 🎉 Тестирование

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Попробуйте команды:
   - `/help` - справка
   - `/stats` - статистика
   - Напишите "яблоко 100г" - поиск продукта
   - Отправьте фото еды - анализ изображения

## 🔧 Health Check

Откройте в браузере:
- Railway: `https://your-railway-app.up.railway.app/health`
- Vercel: `https://your-project.vercel.app/api/health`

Оба должны вернуть статус "ok".

## 💰 Стоимость

- **Railway**: $5 кредитов в месяц (бесплатно)
- **Neon**: 3GB базы данных (бесплатно)
- **Vercel**: неограниченные функции (бесплатно)
- **Langdock**: используете ваши €5 кредитов

## 🆘 Если что-то не работает

### Проверьте логи Railway:
1. Railway → ваш проект → Deployments
2. Кликните на последний деплой
3. Посмотрите логи

### Проверьте логи Vercel:
1. Vercel → ваш проект → Functions
2. Кликните на функцию
3. Посмотрите логи

### Частые проблемы:
- **Бот не отвечает**: проверьте webhook и токен
- **Ошибка базы данных**: проверьте NEON_DATABASE_URL
- **Ошибка анализа фото**: проверьте LANGDOCK_API_KEY

## 🎯 Готово!

Ваш бот работает 24/7 в облаке! Никаких установок на ПК не требуется.

**Ссылки для управления:**
- Railway: https://railway.app
- Vercel: https://vercel.com  
- Neon: https://neon.tech
- GitHub: https://github.com/PLTMisha/nutrition-bot
