# Руководство по Отладке Переменных Окружения Railway

## Описание Проблемы
Переменные сервиса Railway настроены правильно в панели управления, но не загружаются приложением во время выполнения.

## Текущий Статус
✅ Переменные настроены в панели Railway:
- TELEGRAM_BOT_TOKEN
- NEON_DATABASE_URL  
- VERCEL_API_URL
- LANGDOCK_API_KEY
- RAILWAY_ENVIRONMENT
- PORT

❌ Приложение загружает только: railway_environment, port
❌ Отсутствуют: telegram_bot_token, neon_database_url, vercel_api_url

## Примененные Шаги Решения

### 1. Упрощенная Конфигурация railway.toml
```toml
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"

[[services]]
name = "nutrition-bot"

[variables]
PYTHONPATH = "/app"
```

### 2. Добавлено Отладочное Логирование
Добавлено отладочное логирование переменных окружения в `config/settings.py` для просмотра того, что Railway фактически предоставляет.

### 3. Потенциальные Решения для Попытки

#### Вариант A: Использование Railway CLI для Установки Переменных
```bash
railway login
railway link
railway variables set TELEGRAM_BOT_TOKEN=ваш_токен_здесь
railway variables set NEON_DATABASE_URL=ваш_url_бд_здесь
railway variables set VERCEL_API_URL=ваш_vercel_url_здесь
railway variables set LANGDOCK_API_KEY=ваш_langdock_ключ_здесь
```

#### Вариант B: Проверка Области Видимости Переменных
В панели Railway:
1. Перейдите на вкладку Variables
2. Убедитесь, что переменные установлены как "Service Variables", а не "Shared Variables"
3. Проверьте, что они находятся в правильном окружении (production/development)

#### Вариант C: Исправление Чувствительности к Регистру
Railway может быть чувствительным к регистру. Попробуйте установить переменные в нижнем регистре:
- `telegram_bot_token` вместо `TELEGRAM_BOT_TOKEN`
- `neon_database_url` вместо `NEON_DATABASE_URL`
- `vercel_api_url` вместо `VERCEL_API_URL`
- `langdock_api_key` вместо `LANGDOCK_API_KEY`

#### Вариант D: Принудительная Загрузка Переменных Окружения
Добавить в `config/settings.py`:
```python
class Settings(BaseSettings):
    # ... существующие поля ...
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # Принудительная загрузка из окружения
        env_file_encoding = 'utf-8'
        extra = "ignore"
```

#### Вариант E: Ручной Доступ к Переменным Окружения
Заменить настройки Pydantic на прямой доступ к os.environ:
```python
import os

# Прямой доступ к переменным окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('telegram_bot_token')
NEON_DATABASE_URL = os.getenv('NEON_DATABASE_URL') or os.getenv('neon_database_url')
VERCEL_API_URL = os.getenv('VERCEL_API_URL') or os.getenv('vercel_api_url')
LANGDOCK_API_KEY = os.getenv('LANGDOCK_API_KEY') or os.getenv('langdock_api_key')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Переменная окружения TELEGRAM_BOT_TOKEN обязательна")
```

## Следующие Шаги

1. **Развертывание с Отладочным Логированием**: Текущая версия покажет все доступные переменные окружения
2. **Проверка Логов Railway**: Найдите отладочный вывод, чтобы увидеть, какие переменные фактически доступны
3. **Применение Подходящего Решения**: На основе отладочного вывода примените одно из решений выше
4. **Тестирование Развертывания**: Убедитесь, что все необходимые переменные загружаются правильно

## Команды Развертывания Railway

```bash
# Если используете Railway CLI
railway login
railway link
railway deploy

# Проверка логов
railway logs
```

## Ожидаемый Отладочный Вывод

При запуске приложения вы должны увидеть:
```
=== ENVIRONMENT VARIABLES DEBUG ===
RAILWAY_ENVIRONMENT=production
PORT=8000
TELEGRAM_BOT_TOKEN=123456789:ABC...
NEON_DATABASE_URL=postgresql://...
VERCEL_API_URL=https://...
LANGDOCK_API_KEY=sk-...
=== END DEBUG ===
```

Если переменные отсутствуют в этом выводе, проблема в инжекции переменных Railway, а не в коде приложения.

## Дополнительные Советы по Устранению Неполадок

### 1. Проверка Формата Переменных
Убедитесь, что переменные имеют правильный формат:
- `TELEGRAM_BOT_TOKEN`: должен начинаться с цифр, затем двоеточие
- `NEON_DATABASE_URL`: должен начинаться с `postgresql://`
- `VERCEL_API_URL`: должен быть полным URL с `https://`
- `LANGDOCK_API_KEY`: должен начинаться с `sk-`

### 2. Проверка Лимитов Railway
- Убедитесь, что вы не превысили лимиты переменных окружения
- Проверьте, что имена переменных не содержат недопустимых символов

### 3. Очистка Кэша Railway
Попробуйте очистить кэш развертывания:
```bash
railway service delete
railway service create
# Затем заново настройте переменные
```

### 4. Проверка Статуса Сервиса
В панели Railway убедитесь, что:
- Сервис находится в состоянии "Active"
- Нет ошибок в логах развертывания
- Переменные отображаются в разделе Variables

---

**Важно**: После решения проблемы с переменными окружения удалите отладочные print-операторы из `config/settings.py` для продакшена.
