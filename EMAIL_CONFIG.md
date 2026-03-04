# Конфигурация Email-уведомлений

## Настройка в .env файле

Для работы email-уведомлений добавьте следующие переменные в файл `.env`:

```env
# Email Configuration (для Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=error04p@gmail.com
EMAIL_HOST_PASSWORD=yylwzszlqrmniixd

# URL сайта (для ссылок в письмах)
SITE_URL=http://127.0.0.1:8080
```

## Получение пароля приложения Gmail

1. Перейдите: https://myaccount.google.com/security
2. Включите двухфакторную аутентификацию
3. Перейдите: https://myaccount.google.com/apppasswords
4. Создайте пароль приложения для "Почта"
5. Скопируйте 16-значный пароль (без пробелов)
6. Вставьте в `EMAIL_HOST_PASSWORD`

## Альтернатива: Консольный backend (для разработки)

Если не хотите настраивать реальную почту, используйте консольный backend:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

В этом случае письма будут выводиться в консоль терминала.

## Тестирование email-уведомлений

### Через Django shell:
```bash
python manage.py shell
```

```python
from notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='pto_engineer')

# Создаём тестовое уведомление
Notification.objects.create(
    user=user,
    title='Тестовое уведомление',
    message='Это тестовое сообщение для проверки email',
    notification_type='info'
)

# Письмо автоматически отправится благодаря signal
```

### Через мессенджер:
1. Войдите в систему как любой пользователь
2. Откройте виджет мессенджера (кнопка с плюсиком справа внизу)
3. Найдите пользователя и отправьте сообщение
4. Получатель получит email с уведомлением о новом сообщении

## Типы уведомлений, которые отправляются на email:

1. **Новые сообщения в мессенджере**
   - Отправитель
   - Превью сообщения (первые 50 символов)
   - Ссылка на систему

2. **Изменение статуса скважины**
   - Название скважины
   - Новый статус
   - Кто изменил

3. **Новые комментарии к скважине**
   - Автор комментария
   - Текст комментария
   - Ссылка на скважину

4. **Назначение на согласование**
   - Название скважины
   - Кто отправил
   - Дата отправки

## Формат email-сообщений

Все письма имеют:
- ✅ HTML-версию (красивый дизайн)
- ✅ Plain text версию (для старых клиентов)
- ✅ Gradient-заголовок (фиолетовый)
- ✅ Информативное содержание
- ✅ Кнопку "Перейти в систему"
- ✅ Footer с информацией

## Отключение email-уведомлений

Чтобы временно отключить отправку email:

```env
EMAIL_BACKEND=django.core.mail.backends.dummy.EmailBackend
```

Или закомментируйте импорт сигналов в `notifications/apps.py`:

```python
def ready(self):
    # import notifications.signals  # Закомментировать эту строку
    pass
```

## Мониторинг отправки

Все email-уведомления логируются в консоль:
- ✉️ Email отправлен: user@example.com - Тема письма
- ❌ Ошибка отправки email: текст ошибки

## Производительность

- Отправка email происходит синхронно (может замедлить создание уведомлений)
- Используется `fail_silently=True` (ошибки не прерывают работу)
- Для production рекомендуется использовать Celery для асинхронной отправки

## Production настройки

Для production рекомендуется:
1. Использовать сервисы: SendGrid, Mailgun, AWS SES
2. Настроить Celery для асинхронной отправки
3. Включить логирование в файл
4. Добавить retry механизм
5. Мониторить bounce/complaint rate

---

*Документация создана: 22 января 2026*
