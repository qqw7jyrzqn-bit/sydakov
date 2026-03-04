# Скрипт для исправления git состояния и отправки на GitHub

# Отменяем незавершённый rebase
Write-Host "Отмена rebase..."
git rebase --abort

# Проверяем статус
Write-Host ""
Write-Host "Статус репозитория:"
git status

# Добавляем все изменения
Write-Host ""
Write-Host "Добавление изменений..."
git add .

# Создаём коммит с исправлением
Write-Host ""
Write-Host "Создание коммита..."
git commit -m "Fix: Properly handle RAILWAY_DOMAIN environment variable"

# Отправляем на GitHub
Write-Host ""
Write-Host "Отправка на GitHub..."
git push origin main --force-with-lease

Write-Host ""
Write-Host "Готово! Теперь перезапустите деплой на Railway."
