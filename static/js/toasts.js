// Toasts - уведомления в стиле Bootstrap

document.addEventListener('DOMContentLoaded', function() {
    // Обработка кликов по уведомлениям
    const notificationItems = document.querySelectorAll('.notification-item');
    
    notificationItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const notificationId = this.getAttribute('data-notification-id');
            
            if (notificationId) {
                markNotificationAsRead(notificationId);
            }
        });
    });
});

// Пометить уведомление как прочитанное
function markNotificationAsRead(notificationId) {
    fetch(`/notifications/${notificationId}/mark-read/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Обновляем счётчик уведомлений
            updateNotificationBadge(data.unread_count);
            
            // Показываем toast
            showToast('Уведомление прочитано', 'success');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}

// Пометить все уведомления как прочитанные
function markAllAsRead() {
    fetch('/notifications/mark-all-read/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateNotificationBadge(0);
            showToast('Все уведомления прочитаны', 'success');
            location.reload();
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}

// Обновить счётчик уведомлений
function updateNotificationBadge(count) {
    const badge = document.querySelector('.navbar .badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Показать toast-уведомление
function showToast(message, type = 'info') {
    // Создаём контейнер для toasts если его нет
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '11';
        document.body.appendChild(toastContainer);
    }
    
    // Определяем цвет в зависимости от типа
    const bgClass = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    }[type] || 'bg-info';
    
    // Создаём toast
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white ${bgClass} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toastEl);
    
    // Показываем toast
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 3000
    });
    toast.show();
    
    // Удаляем toast после скрытия
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}

// Получить CSRF token из cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Подтверждение действий
function confirmAction(message) {
    return confirm(message || 'Вы уверены?');
}

// AJAX отправка форм
function submitFormAjax(formId, successCallback) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message || 'Успешно!', 'success');
                if (successCallback) {
                    successCallback(data);
                }
            } else {
                showToast(data.message || 'Ошибка!', 'error');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            showToast('Произошла ошибка при выполнении запроса', 'error');
        });
    });
}
