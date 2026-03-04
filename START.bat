@echo off
echo ========================================
echo ЗАПУСК СИСТЕМЫ ИНЖЕНЕРА ПТО
echo ========================================
echo.

cd /d "c:\Users\Никита\Desktop\курсач 3 курс типу\12"

echo  Запуск сервера...
echo.
echo ========================================
echo СЕРВЕР ЗАПУЩЕН!
echo Откройте браузер: http://127.0.0.1:8080/
echo Логин: admin / Пароль: admin
echo ========================================
echo.
cmd /c "venv\Scripts\activate.bat && python manage.py runserver 8080" 

pause
