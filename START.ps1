# БЫСТРЫЙ ЗАПУСК ПРОЕКТА - ОДНА КОМАНДА
# Скопируйте и вставьте эту команду в PowerShell

# Переход в директорию проекта, создание venv, установка зависимостей, миграции, демо-данные и запуск
cd "c:\Users\Никита\Desktop\курсач 3 курс типу\12"; python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt; python manage.py migrate; python manage.py demo_data; python manage.py runserver

# После запуска откройте: http://127.0.0.1:8000/
# Логин: admin / Пароль: admin
