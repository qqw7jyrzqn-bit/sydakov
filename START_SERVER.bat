@echo off
echo ========================================
echo Запуск сервера Django с Python 3.9
echo ========================================
cd /d "%~dp0"

echo Активация виртуального окружения Python 3.9...
call venv_39\Scripts\activate.bat

echo.
echo Проверка версии Python:
python --version

echo.
echo Запуск сервера на порту 8080...
python manage.py runserver 8080
