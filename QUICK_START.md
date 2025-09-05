# ⚡ Быстрый старт Nutrition Bot

## 🚀 За 15 минут до production

### 1. Создайте Telegram бота (2 мин)
```
1. Напишите @BotFather в Telegram
2. /newbot → Nutrition Bot → @your_nutrition_bot
3. Скопируйте токен: 1234567890:AAAA...
```

### 2. Настройте базу данных (3 мин)
```
1. Зайдите на https://neon.tech
2. Sign up with GitHub
3. Create project "nutrition-bot"
4. Скопируйте connection string
```

### 3. Разверните Vercel функции (3 мин)
```bash
npm install -g vercel
cd vercel
vercel login
vercel --prod
# Скопируйте URL: https://your-project.vercel.app
```

### 4. Разверните бота на Railway (5 мин)
```bash
# Загрузите код в GitHub
git init
git add .
git commit -m "Initial commit"
git push origin main

# Зайдите на https://railway.app
# Deploy from GitHub repo
# Добавьте переменные окружения:
TELEGRAM_BOT_TOKEN=ваш_токен
NEON_DATABASE_URL=строка_подключения_neon
VERCEL_API_URL=https://your-project.vercel.app
OPENAI_API_KEY=ваш_openai_ключ
```

### 5. Настройте мониторинг (2 мин)
```
1. Зайдите на https://uptimerobot.com
2. Add Monitor → HTTP(s)
3. URL: https://your-app.up.railway.app/health
4. Interval: 5 minutes
```

## ✅ Готово!

Ваш бот работает 24/7 на бесплатных сервисах:
- 🤖 **Railway**: основной бот
- 🗄️ **Neon**: база данных PostgreSQL
- ⚡ **Vercel**: обработка изображений
- 📊 **UptimeRobot**: мониторинг

## 🧪 Тестирование

Напишите боту:
- `/start` - регистрация
- `яблоко 150г` - поиск продукта
- Отправьте фото штрих-кода
- `/stats` - статистика
- `/lang` - смена языка

## 🔧 Локальная разработка

```bash
# Клонируйте репозиторий
git clone https://github.com/yourusername/nutrition-bot.git
cd nutrition-bot

# Установите зависимости
pip install -r requirements.txt

# Настройте .env
cp .env.example .env
# Отредактируйте .env файл

# Запустите бота
python main.py
```

## 📱 Команды бота

- `/start` - Запуск и регистрация
- `/help` - Справка
- `/stats` - Статистика питания
- `/goal 2000` - Установить цель калорий
- `/history` - История записей
- `/clear` - Очистить данные за день
- `/lang` - Изменить язык

## 🌍 Поддерживаемые языки

- 🇺🇸 English
- 🇷🇺 Русский
- 🇺🇦 Українська

## 💡 Возможности

✅ **Поиск продуктов** - просто напишите "хлеб 50г"
✅ **Сканирование штрих-кодов** - отправьте фото кода
✅ **Анализ блюд по фото** - с эталонными объектами
✅ **Статистика БЖУ** - дневная, недельная, месячная
✅ **Мультиязычность** - автоматическое определение языка
✅ **Цели калорий** - персональные настройки

## 🆘 Помощь

**Проблемы с развертыванием?**
- Проверьте переменные окружения
- Посмотрите логи: `railway logs`
- Health check: `curl https://your-app.up.railway.app/health`

**Бот не отвечает?**
- Проверьте токен бота
- Убедитесь что Railway приложение запущено
- Проверьте подключение к базе данных

**Ошибки с изображениями?**
- Проверьте OpenAI API ключ
- Убедитесь что Vercel функции развернуты
- Размер изображения должен быть < 20MB

## 📞 Поддержка

- 📖 Полная документация: `DEPLOYMENT_GUIDE.md`
- 🐛 Сообщить об ошибке: создайте Issue в GitHub
- 💬 Вопросы: обратитесь к разработчику

---

**Готово! Ваш Nutrition Bot работает в production! 🎉**
