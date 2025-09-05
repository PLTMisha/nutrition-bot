# 📤 Точный список файлов для загрузки в GitHub

## 🎯 Быстрый способ: Выделить и перетащить

### 📁 Корневые файлы (обязательные):
```
main.py
requirements.txt
railway.toml
Dockerfile
README.md
.env.example
```

### 📁 Папка config/ (целиком):
```
config/
├── __init__.py
├── database.py
└── settings.py
```

### 📁 Папка handlers/ (целиком):
```
handlers/
├── __init__.py
├── basic.py
├── food_search.py
├── media.py
└── nutrition.py
```

### 📁 Папка models/ (целиком):
```
models/
├── __init__.py
└── db_models.py
```

### 📁 Папка services/ (целиком):
```
services/
├── __init__.py
├── database_service.py
├── openfoodfacts.py
└── vercel_api.py
```

### 📁 Папка utils/ (целиком):
```
utils/
├── __init__.py
├── cache.py
├── helpers.py
├── i18n.py
├── keyboards.py
├── language_middleware.py
├── middleware.py
├── rate_limiter.py
└── validators.py
```

### 📁 Папка vercel/ (целиком):
```
vercel/
├── vercel.json
├── requirements.txt
├── api/
│   ├── analyze-photo.py
│   ├── analyze-photo-langdock.py
│   ├── process-barcode.py
│   └── health.py
└── utils/
    ├── __init__.py
    ├── image_processing.py
    └── nutrition_calc.py
```

### 📁 Документация (рекомендуется):
```
DEPLOYMENT_GUIDE.md
QUICK_START.md
CLOUD_ONLY_SETUP.md
GITHUB_UPLOAD.md
LANGDOCK_SETUP.md
NPM_FIX.md
```

## 🚫 НЕ загружайте эти файлы:
```
.env (если есть - содержит секретные ключи!)
__pycache__/ (папки с кэшем)
.git/ (если есть)
node_modules/ (если есть)
*.pyc (файлы кэша Python)
.DS_Store (macOS)
Thumbs.db (Windows)
```

## ⚡ Самый быстрый способ:

### Вариант 1: Выделить все сразу
1. Откройте папку `d:/FoodAIBotTg`
2. Выделите **ВСЕ файлы и папки** (Ctrl+A)
3. **ИСКЛЮЧИТЕ** только `.env` (если есть) и `__pycache__`
4. Перетащите в GitHub

### Вариант 2: По частям (если много файлов)
1. **Сначала корневые файлы:**
   - `main.py`, `requirements.txt`, `railway.toml`, `Dockerfile`, `README.md`, `.env.example`

2. **Затем папки по одной:**
   - Перетащите папку `config/`
   - Перетащите папку `handlers/`
   - Перетащите папку `models/`
   - Перетащите папку `services/`
   - Перетащите папку `utils/`
   - Перетащите папку `vercel/`

3. **Документацию (опционально):**
   - Все `.md` файлы

## 📋 Пошаговая инструкция:

### Шаг 1: Создайте репозиторий
1. Зайдите на https://github.com
2. Нажмите **"New repository"**
3. Название: `nutrition-bot`
4. Описание: `Telegram bot for nutrition tracking with Langdock AI`
5. **Public** (для бесплатного аккаунта)
6. ✅ **Add a README file**
7. **Create repository**

### Шаг 2: Загрузите файлы
1. В репозитории нажмите **"uploading an existing file"**
2. **Перетащите ВСЕ файлы** из `d:/FoodAIBotTg` в окно браузера
3. Или нажмите **"choose your files"** и выберите все

### Шаг 3: Подтвердите
1. Commit message: `Initial commit - Nutrition Bot with Langdock support`
2. **Commit changes**

## ✅ Проверка после загрузки:

В репозитории должны быть:
- ✅ `main.py` (основной файл бота)
- ✅ `requirements.txt` (зависимости Python)
- ✅ `railway.toml` (конфигурация Railway)
- ✅ Папка `vercel/` с файлами внутри
- ✅ Папки `config/`, `handlers/`, `models/`, `services/`, `utils/`
- ✅ Документация `.md` файлы

## 🚀 После загрузки:

1. **Скопируйте URL репозитория:**
   ```
   https://github.com/ваш_username/nutrition-bot
   ```

2. **Переходите к развертыванию:**
   - Следуйте `CLOUD_ONLY_SETUP.md`
   - Используйте этот репозиторий в Railway и Vercel

## 💡 Полезные советы:

### Если файлы не загружаются:
- Попробуйте загружать по частям
- Проверьте размер файлов (макс 100MB каждый)
- Обновите страницу и попробуйте снова

### Если нужно обновить файлы:
1. Зайдите в файл в GitHub
2. Нажмите **"Edit"** (карандаш)
3. Внесите изменения
4. **Commit changes**

### Для Langdock:
После загрузки в GitHub переименуйте в папке `vercel/api/`:
- `analyze-photo.py` → `analyze-photo-openai.py`
- `analyze-photo-langdock.py` → `analyze-photo.py`

---

**Готово! Теперь ваш код в GitHub и готов к развертыванию! 🎉**
