# 📤 Как загрузить код в GitHub через браузер

## 🎯 Цель: Загрузить все файлы проекта в GitHub без Git

## 📋 Пошаговая инструкция:

### Шаг 1: Создайте репозиторий
1. Зайдите на https://github.com
2. Нажмите зеленую кнопку **"New"** (или плюс → New repository)
3. Repository name: `nutrition-bot`
4. Description: `Telegram bot for nutrition tracking`
5. Выберите **Public** (для бесплатного аккаунта)
6. ✅ Поставьте галочку **"Add a README file"**
7. Нажмите **"Create repository"**

### Шаг 2: Загрузите файлы
1. В созданном репозитории нажмите **"uploading an existing file"**
2. Перетащите ВСЕ файлы из папки `d:/FoodAIBotTg` в окно браузера
3. Или нажмите **"choose your files"** и выберите все файлы

### Шаг 3: Подтвердите загрузку
1. В поле "Commit changes" напишите: `Initial commit - Nutrition Bot`
2. Нажмите **"Commit changes"**

## 📁 Какие файлы загружать:

### ✅ Обязательные файлы:
```
main.py
requirements.txt
railway.toml
Dockerfile
README.md
DEPLOYMENT_GUIDE.md
QUICK_START.md
CLOUD_ONLY_SETUP.md
.env.example
```

### ✅ Папки целиком:
```
config/
handlers/
models/
services/
utils/
vercel/
```

### ❌ НЕ загружайте:
```
.env (если есть - содержит секретные ключи)
__pycache__/ (папки с кэшем Python)
.git/ (если есть)
node_modules/ (если есть)
```

## 🔍 Проверка загрузки:

После загрузки в репозитории должны быть:
- ✅ Файл `main.py`
- ✅ Папка `vercel/` с файлами внутри
- ✅ Папка `config/` с настройками
- ✅ Файл `requirements.txt`
- ✅ Все остальные файлы проекта

## 🚀 Что дальше:

1. **Скопируйте URL репозитория** (например: `https://github.com/username/nutrition-bot`)
2. Переходите к развертыванию на Railway
3. При создании проекта на Railway выберите ваш репозиторий

## 💡 Альтернативный способ:

### Через GitHub Desktop (если хотите):
1. Скачайте GitHub Desktop
2. Clone repository → ваш репозиторий
3. Скопируйте файлы в локальную папку
4. Commit → Push

### Через командную строку (если умеете):
```bash
git clone https://github.com/username/nutrition-bot.git
cd nutrition-bot
# Скопируйте файлы сюда
git add .
git commit -m "Initial commit"
git push
```

## 🆘 Если возникли проблемы:

### Файлы не загружаются:
- Попробуйте загружать по частям (сначала основные файлы, потом папки)
- Убедитесь что размер файлов < 100MB каждый

### Ошибка при загрузке:
- Обновите страницу и попробуйте снова
- Проверьте интернет-соединение

### Не видите кнопку "uploading an existing file":
- Убедитесь что репозиторий пустой
- Или нажмите "Add file" → "Upload files"

## ✅ Готово!

После успешной загрузки ваш код будет доступен в GitHub и готов для развертывания на Railway и Vercel!

---

**Следующий шаг: используйте `CLOUD_ONLY_SETUP.md` для развертывания в облаке**
