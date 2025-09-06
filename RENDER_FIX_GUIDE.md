# 🔧 Исправление проблем развертывания на Render

## ❌ Проблема: Ошибка сборки Pillow с Python 3.13

**Ошибка:**
```
KeyError: '__version__'
Getting requirements to build wheel did not run successfully.
```

## ✅ Решение:

### Вариант 1: Использовать минимальные зависимости (РЕКОМЕНДУЕТСЯ)
Используйте файл `requirements-render.txt` вместо `requirements.txt`:

1. В настройках Render измените **Build Command** на:
   ```bash
   pip install -r requirements-render.txt
   ```

### Вариант 2: Указать версию Python
Добавьте файл `runtime.txt` в корень проекта:
```
python-3.11.9
```

### Вариант 3: Обновить render.yaml
```yaml
services:
  - type: web
    name: nutrition-bot
    env: python
    buildCommand: pip install -r requirements-render.txt
    startCommand: python main.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
```

## 🚀 Быстрое исправление:

1. **Загрузите изменения в GitHub**:
   ```bash
   git add requirements-render.txt
   git commit -m "Add minimal requirements for Render"
   git push
   ```

2. **В панели Render**:
   - Перейдите в настройки вашего сервиса
   - Измените **Build Command** на: `pip install -r requirements-render.txt`
   - Нажмите **Save Changes**
   - Запустите **Manual Deploy**

## 📋 Что исключено из requirements-render.txt:

- `pandas` и `matplotlib` - тяжелые библиотеки, не критичные для работы
- `alembic` - миграции БД (можно добавить позже)
- Development зависимости (`pytest`, `black`, `flake8`)

## ✅ Результат:

После применения исправления деплой должен пройти успешно. Бот будет работать со всеми основными функциями:
- Telegram API
- База данных Neon
- Обработка изображений
- API вызовы к Vercel/Langdock

## 🔄 Если проблема остается:

1. Попробуйте указать Python 3.11 в `runtime.txt`
2. Очистите кэш Render (в настройках сервиса)
3. Проверьте логи сборки на наличие других ошибок

## 📞 Дополнительная помощь:

Если ошибка повторяется, проверьте:
- Все переменные окружения настроены правильно
- GitHub репозиторий содержит все необходимые файлы
- Нет конфликтов в зависимостях
