#!/usr/bin/env python3
"""
Автоматическая настройка Nutrition Bot
Этот скрипт поможет быстро настроить все необходимые компоненты
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional

class NutritionBotSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / ".env"
        self.config = {}
        
    def print_header(self):
        """Печать заголовка"""
        print("=" * 60)
        print("🍎 NUTRITION BOT - АВТОМАТИЧЕСКАЯ НАСТРОЙКА")
        print("=" * 60)
        print()
        
    def print_step(self, step: int, title: str):
        """Печать шага настройки"""
        print(f"\n📋 Шаг {step}: {title}")
        print("-" * 40)
        
    def get_user_input(self, prompt: str, required: bool = True) -> Optional[str]:
        """Получение ввода от пользователя"""
        while True:
            value = input(f"➤ {prompt}: ").strip()
            if value or not required:
                return value if value else None
            print("❌ Это поле обязательно для заполнения!")
            
    def check_dependencies(self):
        """Проверка зависимостей"""
        self.print_step(1, "Проверка зависимостей")
        
        # Основные зависимости (обязательные)
        core_dependencies = {
            "python": "python --version",
            "pip": "pip --version",
            "git": "git --version"
        }
        
        # Дополнительные зависимости (для Vercel)
        optional_dependencies = {
            "node": "node --version",
            "npm": "npm --version"
        }
        
        missing_core = []
        missing_optional = []
        
        # Проверяем основные зависимости
        for name, command in core_dependencies.items():
            try:
                result = subprocess.run(command.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    print(f"✅ {name}: {version}")
                else:
                    missing_core.append(name)
            except FileNotFoundError:
                missing_core.append(name)
        
        # Проверяем дополнительные зависимости
        for name, command in optional_dependencies.items():
            try:
                result = subprocess.run(command.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    print(f"✅ {name}: {version}")
                else:
                    missing_optional.append(name)
            except FileNotFoundError:
                missing_optional.append(name)
        
        # Если отсутствуют основные зависимости - останавливаем
        if missing_core:
            print(f"\n❌ Отсутствуют обязательные зависимости: {', '.join(missing_core)}")
            print("\nУстановите их перед продолжением:")
            for dep in missing_core:
                if dep == "python":
                    print("- Python 3.9+: https://python.org/downloads/")
                elif dep == "git":
                    print("- Git: https://git-scm.com/downloads")
            return False
        
        # Если отсутствуют дополнительные зависимости - предупреждаем
        if missing_optional:
            print(f"\n⚠️ Отсутствуют дополнительные зависимости: {', '.join(missing_optional)}")
            print("Это не критично - Vercel функции можно развернуть позже")
            if "npm" in missing_optional:
                print("\n💡 Для установки npm:")
                print("1. Переустановите Node.js с https://nodejs.org/")
                print("2. Или добавьте npm в PATH вручную")
                print("3. Перезапустите командную строку")
            self.has_npm = False
        else:
            self.has_npm = True
            
        return True
        
    def setup_telegram_bot(self):
        """Настройка Telegram бота"""
        self.print_step(2, "Настройка Telegram бота")
        
        print("1. Откройте Telegram и найдите @BotFather")
        print("2. Отправьте команду: /newbot")
        print("3. Следуйте инструкциям для создания бота")
        print("4. Скопируйте токен бота")
        print()
        
        token = self.get_user_input("Введите токен Telegram бота")
        self.config["TELEGRAM_BOT_TOKEN"] = token
        
        print("✅ Telegram бот настроен")
        
    def setup_database(self):
        """Настройка базы данных"""
        self.print_step(3, "Настройка базы данных Neon PostgreSQL")
        
        print("1. Перейдите на https://neon.tech")
        print("2. Зарегистрируйтесь через GitHub")
        print("3. Создайте новый проект 'nutrition-bot'")
        print("4. Скопируйте строку подключения")
        print()
        
        db_url = self.get_user_input("Введите строку подключения к базе данных")
        self.config["NEON_DATABASE_URL"] = db_url
        
        print("✅ База данных настроена")
        
    def setup_openai(self):
        """Настройка OpenAI API"""
        self.print_step(4, "Настройка OpenAI API")
        
        print("1. Перейдите на https://platform.openai.com/api-keys")
        print("2. Создайте новый API ключ")
        print("3. Скопируйте ключ")
        print()
        
        api_key = self.get_user_input("Введите OpenAI API ключ")
        self.config["OPENAI_API_KEY"] = api_key
        
        print("✅ OpenAI API настроен")
        
    def setup_vercel(self):
        """Настройка Vercel"""
        self.print_step(5, "Развертывание Vercel функций")
        
        if not hasattr(self, 'has_npm') or not self.has_npm:
            print("❌ npm не найден. Для развертывания Vercel функций нужен npm.")
            print("\n📋 Инструкции для ручного развертывания:")
            print("1. Установите Node.js с npm: https://nodejs.org/")
            print("2. Перезапустите командную строку")
            print("3. Выполните команды:")
            print("   npm install -g vercel")
            print("   cd vercel")
            print("   vercel login")
            print("   vercel --prod")
            print("\n⏭️ Пропускаем автоматическое развертывание Vercel")
            return
        
        try:
            # Проверяем установлен ли Vercel CLI
            subprocess.run(["vercel", "--version"], capture_output=True, check=True)
            print("✅ Vercel CLI уже установлен")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📦 Устанавливаем Vercel CLI...")
            try:
                subprocess.run(["npm", "install", "-g", "vercel"], check=True)
                print("✅ Vercel CLI установлен")
            except subprocess.CalledProcessError as e:
                print(f"❌ Ошибка установки Vercel CLI: {e}")
                return
            
        print("\n1. Войдите в аккаунт Vercel:")
        try:
            subprocess.run(["vercel", "login"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Ошибка входа в Vercel")
            return
        
        print("\n2. Развертываем функции...")
        vercel_dir = self.project_root / "vercel"
        original_dir = os.getcwd()
        
        try:
            os.chdir(vercel_dir)
            result = subprocess.run(["vercel", "--prod"], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Извлекаем URL из вывода
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'https://' in line and 'vercel.app' in line:
                        vercel_url = line.strip()
                        self.config["VERCEL_API_URL"] = vercel_url
                        print(f"✅ Vercel функции развернуты: {vercel_url}")
                        break
                else:
                    print("⚠️ Vercel развернут, но URL не найден в выводе")
                    print("Проверьте URL в панели Vercel")
            else:
                print("❌ Ошибка развертывания Vercel функций")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                
        except Exception as e:
            print(f"❌ Ошибка при развертывании: {e}")
        finally:
            os.chdir(original_dir)
        
    def create_env_file(self):
        """Создание .env файла"""
        self.print_step(6, "Создание .env файла")
        
        env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={self.config.get('TELEGRAM_BOT_TOKEN', '')}

# Database Configuration
NEON_DATABASE_URL={self.config.get('NEON_DATABASE_URL', '')}

# External APIs
OPENAI_API_KEY={self.config.get('OPENAI_API_KEY', '')}
VERCEL_API_URL={self.config.get('VERCEL_API_URL', '')}

# Environment Settings
RAILWAY_ENVIRONMENT=development
PORT=8000
LOG_LEVEL=INFO

# Optional Services
REDIS_URL=
SENTRY_DSN=
"""
        
        with open(self.env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
            
        print(f"✅ Файл .env создан: {self.env_file}")
        
    def install_dependencies(self):
        """Установка Python зависимостей"""
        self.print_step(7, "Установка зависимостей")
        
        print("Устанавливаем Python пакеты...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        print("✅ Зависимости установлены")
        
    def test_local_setup(self):
        """Тестирование локальной настройки"""
        self.print_step(8, "Тестирование настройки")
        
        print("Проверяем подключение к базе данных...")
        try:
            # Импортируем и тестируем подключение
            from config.database import init_database, create_tables
            import asyncio
            
            async def test_db():
                await init_database()
                await create_tables()
                print("✅ Подключение к базе данных успешно")
                
            asyncio.run(test_db())
            
        except Exception as e:
            print(f"❌ Ошибка подключения к базе данных: {e}")
            
    def setup_railway_instructions(self):
        """Инструкции для Railway"""
        self.print_step(9, "Развертывание на Railway")
        
        print("Для развертывания на Railway выполните:")
        print()
        print("1. Загрузите код в GitHub:")
        print("   git init")
        print("   git add .")
        print("   git commit -m 'Initial commit'")
        print("   git remote add origin https://github.com/username/nutrition-bot.git")
        print("   git push -u origin main")
        print()
        print("2. Перейдите на https://railway.app")
        print("3. Deploy from GitHub repo")
        print("4. Добавьте переменные окружения из .env файла")
        print()
        
    def setup_monitoring_instructions(self):
        """Инструкции для мониторинга"""
        self.print_step(10, "Настройка мониторинга")
        
        print("Для настройки мониторинга:")
        print()
        print("1. Перейдите на https://uptimerobot.com")
        print("2. Создайте бесплатный аккаунт")
        print("3. Add Monitor → HTTP(s)")
        print("4. URL: https://your-app.up.railway.app/health")
        print("5. Monitoring Interval: 5 minutes")
        print()
        
    def print_summary(self):
        """Печать итогов"""
        print("\n" + "=" * 60)
        print("🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
        print("=" * 60)
        print()
        print("📁 Созданные файлы:")
        print(f"   - {self.env_file}")
        print()
        print("🚀 Для запуска бота локально:")
        print("   python main.py")
        print()
        print("📖 Дополнительная документация:")
        print("   - DEPLOYMENT_GUIDE.md - полное руководство")
        print("   - QUICK_START.md - быстрый старт")
        print("   - README.md - описание проекта")
        print()
        print("🆘 Нужна помощь?")
        print("   - Проверьте health check: curl http://localhost:8000/health")
        print("   - Посмотрите логи в консоли")
        print("   - Обратитесь к документации")
        print()
        
    def run(self):
        """Запуск процесса настройки"""
        try:
            self.print_header()
            
            if not self.check_dependencies():
                return False
                
            self.setup_telegram_bot()
            self.setup_database()
            self.setup_openai()
            
            # Vercel setup (опционально)
            if hasattr(self, 'has_npm') and self.has_npm:
                setup_vercel = input("\n❓ Развернуть Vercel функции сейчас? (y/n): ").lower() == 'y'
                if setup_vercel:
                    self.setup_vercel()
                else:
                    print("⏭️ Пропускаем развертывание Vercel (можно сделать позже)")
            else:
                print("\n⏭️ Пропускаем развертывание Vercel (npm не найден)")
                print("📋 Для ручного развертывания позже:")
                print("1. Установите Node.js с npm")
                print("2. Выполните: npm install -g vercel")
                print("3. Перейдите в папку vercel и выполните: vercel --prod")
                
            self.create_env_file()
            self.install_dependencies()
            
            # Тестирование (опционально)
            test_setup = input("\n❓ Протестировать настройку? (y/n): ").lower() == 'y'
            if test_setup:
                self.test_local_setup()
                
            self.setup_railway_instructions()
            self.setup_monitoring_instructions()
            self.print_summary()
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n❌ Настройка прервана пользователем")
            return False
        except Exception as e:
            print(f"\n\n❌ Ошибка настройки: {e}")
            return False


if __name__ == "__main__":
    setup = NutritionBotSetup()
    success = setup.run()
    sys.exit(0 if success else 1)
