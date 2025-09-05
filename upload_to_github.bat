@echo off
echo ========================================
echo  АВТОМАТИЧЕСКАЯ ЗАГРУЗКА В GITHUB
echo ========================================
echo.

REM Проверяем наличие git
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git не найден! Установите Git с https://git-scm.com/downloads
    pause
    exit /b 1
)

echo ✅ Git найден
echo.

REM Запрашиваем данные у пользователя
set /p GITHUB_USERNAME="Введите ваш GitHub username: "
set /p REPO_NAME="Введите название репозитория (по умолчанию nutrition-bot): "
if "%REPO_NAME%"=="" set REPO_NAME=nutrition-bot

echo.
echo 📋 Настройки:
echo Username: %GITHUB_USERNAME%
echo Repository: %REPO_NAME%
echo.

set /p CONFIRM="Продолжить? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Отменено пользователем
    pause
    exit /b 0
)

echo.
echo 🚀 Начинаем загрузку...
echo.

REM Инициализируем git репозиторий
echo 📁 Инициализация git...
git init
if errorlevel 1 (
    echo ❌ Ошибка инициализации git
    pause
    exit /b 1
)

REM Создаем .gitignore
echo 📝 Создание .gitignore...
echo .env > .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo .DS_Store >> .gitignore
echo Thumbs.db >> .gitignore
echo node_modules/ >> .gitignore

REM Добавляем все файлы
echo 📤 Добавление файлов...
git add .
if errorlevel 1 (
    echo ❌ Ошибка добавления файлов
    pause
    exit /b 1
)

REM Делаем первый коммит
echo 💾 Создание коммита...
git commit -m "Initial commit - Nutrition Bot with Langdock support"
if errorlevel 1 (
    echo ❌ Ошибка создания коммита
    pause
    exit /b 1
)

REM Переименовываем ветку в main
echo 🌿 Настройка ветки main...
git branch -M main

REM Добавляем remote origin
echo 🔗 Подключение к GitHub...
git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
if errorlevel 1 (
    echo ❌ Ошибка подключения к GitHub
    echo Убедитесь что репозиторий %REPO_NAME% существует в вашем GitHub аккаунте
    pause
    exit /b 1
)

REM Пушим в GitHub
echo 🚀 Загрузка в GitHub...
echo.
echo ⚠️  Сейчас откроется окно для ввода логина и пароля GitHub
echo    Используйте Personal Access Token вместо пароля!
echo.
git push -u origin main
if errorlevel 1 (
    echo ❌ Ошибка загрузки в GitHub
    echo.
    echo 💡 Возможные причины:
    echo    - Репозиторий не существует
    echo    - Неправильные учетные данные
    echo    - Нужен Personal Access Token вместо пароля
    echo.
    echo 🔧 Создайте Personal Access Token:
    echo    1. GitHub → Settings → Developer settings → Personal access tokens
    echo    2. Generate new token (classic)
    echo    3. Выберите repo permissions
    echo    4. Используйте токен вместо пароля
    pause
    exit /b 1
)

echo.
echo ✅ УСПЕШНО ЗАГРУЖЕНО!
echo.
echo 🎉 Ваш код загружен в GitHub:
echo    https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo.
echo 📋 Следующие шаги:
echo    1. Проверьте репозиторий в браузере
echo    2. Следуйте инструкции CLOUD_ONLY_SETUP.md
echo    3. Разверните на Railway и Vercel
echo.
pause
