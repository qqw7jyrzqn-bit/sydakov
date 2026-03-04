@echo off
echo ========================================
echo УСТАНОВКА ОКРУЖЕНИЯ (Python 3.9)
echo ========================================
echo.

cd /d "c:\Users\Никита\Desktop\курсач 3 курс типу\12"

REM Создаём виртуальное окружение с Python 3.9
if not exist venv_39 (
    echo Создание виртуального окружения с Python 3.9...
    py -3.9 -m venv venv_39
    echo.
    echo Установка зависимостей...
    venv_39\Scripts\python.exe -m pip install --upgrade pip
    venv_39\Scripts\python.exe -m pip install -r requirements.txt
    echo.
)

echo ========================================
echo ЗАПУСК СИСТЕМЫ ИНЖЕНЕРА ПТО
echo ========================================
echo.

echo  Запуск сервера на Python 3.9...
echo.
echo ========================================
echo СЕРВЕР ЗАПУЩЕН!
echo Откройте браузер: http://127.0.0.1:8080/
echo Логин: admin / Пароль: admin
echo ========================================
echo.

venv_39\Scripts\python.exe manage.py runserver 8080

pause
