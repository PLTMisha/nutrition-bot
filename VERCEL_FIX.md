# 🔧 Исправление ошибки Vercel

## ❌ Ошибка:
```
Environment Variable "LANGDOCK_API_KEY" references Secret "langdock_api_key", which does not exist.
```

## ✅ Решение:

### Проблема была в файле `vercel.json`
Мы использовали синтаксис `@langdock_api_key`, который ссылается на секрет Vercel, но этот секрет не был создан.

### Что исправлено:
1. **Удалена секция `env` из `vercel.json`** - переменные окружения теперь добавляются только через интерфейс Vercel
2. **Обновлена инструкция** - добавлены подробные шаги по добавлению переменных

### Как правильно добавить переменные в Vercel:

1. **Зайдите в ваш проект на Vercel**
2. **Settings → Environment Variables**
3. **Нажмите "Add New"** для каждой переменной:

#### Переменная 1:
- **Name:** `LANGDOCK_API_KEY`
- **Value:** ваш реальный ключ от Langdock (без кавычек)
- **Environment:** выберите все (Production, Preview, Development)

#### Переменная 2:
- **Name:** `LANGDOCK_BASE_URL`
- **Value:** `https://api.langdock.com/v1`
- **Environment:** выберите все

#### Переменная 3:
- **Name:** `OPENFOODFACTS_API_URL`
- **Value:** `https://world.openfoodfacts.org/api`
- **Environment:** выберите все

4. **Нажмите "Save"** после каждой переменной
5. **Нажмите "Redeploy"** для применения изменений

## 🚀 Теперь деплой должен пройти успешно!

После этих изменений Vercel сможет развернуть функции без ошибок.

## 📝 Что изменилось в коде:

**Было в `vercel.json`:**
```json
"env": {
  "LANGDOCK_API_KEY": "@langdock_api_key",
  "LANGDOCK_BASE_URL": "https://api.langdock.com/v1",
  "OPENFOODFACTS_API_URL": "https://world.openfoodfacts.org/api"
}
```

**Стало:**
```json
// Секция env полностью удалена
// Переменные добавляются через интерфейс Vercel
```

## ✅ Проверка:
После успешного деплоя откройте:
`https://your-project.vercel.app/api/health`

Должен вернуться ответ: `{"status": "ok"}`
