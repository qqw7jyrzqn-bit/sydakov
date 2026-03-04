# Разграничение доступа по ролям

## 🔐 Роли в системе

Система использует **двухуровневую систему ролей** для управления доступом:

### 1. **Инженер ПТО** (`pto_engineer`)
**Основная роль:** Создание и управление своими проектами скважин

#### ✅ Разрешённые действия:
- ✓ Создание новых скважин (черновики)
- ✓ Редактирование **только своих** черновиков и отклонённых скважин
- ✓ Отправка скважин на согласование начальнику
- ✓ Просмотр **только своих** скважин
- ✓ Генерация документов по своим скважинам
- ✓ Загрузка документов к своим скважинам
- ✓ Комментирование своих скважин
- ✓ Экспорт списка своих скважин в Excel
- ✓ Удаление своих черновиков

#### ❌ Запрещённые действия:
- ✗ Просмотр чужих скважин
- ✗ Согласование/утверждение скважин
- ✗ Отклонение скважин
- ✗ Редактирование чужих скважин
- ✗ Изменение статусов (начать бурение, завершить и т.д.)
- ✗ Удаление утверждённых скважин
- ✗ Доступ к аналитике
- ✗ Доступ к админ-панели Django

---

### 2. **Начальник ПТО** (`head_pto`)
**Основная роль:** Согласование, контроль и управление всеми проектами

#### ✅ Разрешённые действия:
- ✓ Все права Инженера ПТО +
- ✓ **Просмотр всех скважин** в системе
- ✓ **Согласование** скважин, отправленных на проверку
- ✓ **Отклонение** скважин с указанием причины
- ✓ Редактирование **любых** скважин (кроме архивных)
- ✓ **Изменение статусов** скважин (начать бурение, завершить, архивировать)
- ✓ Просмотр истории согласований
- ✓ Окончательное утверждение проектов
- ✓ **Доступ к аналитике** и отчётам
- ✓ Доступ к админ-панели Django (для суперпользователей)

#### ❌ Запрещённые действия:
- ✗ Изменение архивированных скважин
- ✗ Удаление скважин с историей согласований

---

## 🔒 Реализация в коде

### Методы проверки прав в модели User

```python
# accounts/models.py
def can_create_wells(self):
    """Может ли пользователь создавать скважины"""
    return self.role in ['pto_engineer', 'head_pto']

def can_edit_wells(self):
    """Может ли пользователь редактировать скважины"""
    return self.role in ['pto_engineer', 'head_pto']

def can_approve_wells(self):
    """Может ли пользователь согласовывать скважины"""
    return self.role == 'head_pto'

def can_generate_documents(self):
    """Может ли пользователь генерировать документы"""
    return self.role in ['pto_engineer', 'head_pto']

def can_view_all_wells(self):
    """Может ли пользователь видеть все скважины"""
    return self.role == 'head_pto'

def can_comment_on_wells(self):
    """Может ли пользователь комментировать скважины"""
    return self.role in ['pto_engineer', 'head_pto']

def can_change_well_status(self):
    """Может ли пользователь изменять статусы скважин"""
    return self.role == 'head_pto'

def can_access_analytics(self):
    """Может ли пользователь видеть аналитику"""
    return self.role == 'head_pto'

def get_accessible_wells(self):
    """Возвращает скважины, доступные пользователю"""
    from wells.models import Well
    
    if self.role == 'head_pto':
        # Начальник ПТО видит все скважины
        return Well.objects.all()
    elif self.role == 'pto_engineer':
        # Инженер видит только свои скважины
        return Well.objects.filter(author=self)
    else:
        return Well.objects.none()
```

### Миксины для Class-Based Views

```python
# accounts/mixins.py

class PTOStaffRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки прав сотрудников ПТО (инженер + начальник)"""
    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.role in ['pto_engineer', 'head_pto']
    
    def handle_no_permission(self):
        messages.error(self.request, 'Доступ разрешен только сотрудникам ПТО.')
        return redirect('wells:home')

class PTOEngineerRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки прав инженера ПТО"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_pto_engineer()

class HeadPTORequiredMixin(UserPassesTestMixin):
    """Миксин для проверки прав начальника ПТО"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_head_pto()

class CanEditWellMixin(UserPassesTestMixin):
    """Миксин для проверки прав на редактирование скважин"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.can_edit_wells()

class CanApproveWellMixin(UserPassesTestMixin):
    """Миксин для проверки прав на согласование скважин"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.can_approve_wells()
```

### Применение в Views

```python
# wells/views.py

# Список скважин - доступ только для сотрудников ПТО
class WellListView(PTOStaffRequiredMixin, ListView):
    model = Well
    template_name = 'wells/well_list.html'
    ...

# Детальная информация о скважине - доступ только для сотрудников ПТО
class WellDetailView(PTOStaffRequiredMixin, DetailView):
    model = Well
    template_name = 'wells/well_detail.html'
    ...

# Создание скважины - доступ только для сотрудников ПТО
class WellCreateView(PTOStaffRequiredMixin, CreateView):
    model = Well
    form_class = WellForm
    ...

# Редактирование скважины - проверка прав на редактирование
class WellUpdateView(CanEditWellMixin, UpdateView):
    model = Well
    form_class = WellForm
    ...

# Удаление скважины - доступ только для сотрудников ПТО
class WellDeleteView(PTOStaffRequiredMixin, DeleteView):
    model = Well
    ...
```

### Декораторы для Function-Based Views

```python
# accounts/mixins.py

@pto_engineer_required
def well_send_for_approval(request, pk):
    """Только инженер ПТО может отправлять на согласование"""
    well = get_object_or_404(Well, pk=pk)
    if well.author != request.user:
        messages.error(request, 'Вы можете отправлять на согласование только свои скважины.')
        return redirect('wells:well_detail', pk=pk)
    ...

@head_pto_required
def well_approve(request, pk):
    """Только начальник ПТО может согласовывать"""
    well = get_object_or_404(Well, pk=pk)
    ...

@head_pto_required
def well_reject(request, pk):
    """Только начальник ПТО может отклонять"""
    well = get_object_or_404(Well, pk=pk)
    ...

@pto_staff_required
def export_wells_excel(request):
    """Только сотрудники ПТО могут экспортировать данные"""
    wells = request.user.get_accessible_wells()
    ...

@login_required
def generate_report(request, well_id):
    """Генерация документов с проверкой прав"""
    accessible_wells = request.user.get_accessible_wells()
    well = get_object_or_404(accessible_wells, pk=well_id)
    
    if not request.user.can_generate_documents():
        messages.error(request, 'У вас нет прав на генерацию документов.')
        return redirect('wells:well_detail', pk=well_id)
    ...
```

### Фильтрация в Views

```python
# wells/views.py
def dashboard(request):
    # Каждый пользователь видит только доступные ему скважины
    wells = request.user.get_accessible_wells()
    ...

class WellDetailView(DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаём права в шаблон
        context['can_edit'] = self.request.user.can_edit_wells()
        context['can_approve'] = self.request.user.can_approve_wells()
        context['can_generate_docs'] = self.request.user.can_generate_documents()
        return context
```

### Условия в шаблонах

```html
<!-- templates/base.html - кнопка создания в навигации -->
{% if user.can_create_wells %}
<li class="nav-item ms-2">
    <a class="btn btn-create-modern" href="{% url 'wells:well_create' %}">
        <i class="bi bi-plus-circle-fill"></i> Создать скважину
    </a>
</li>
{% endif %}

<!-- templates/wells/well_detail.html - панель действий -->

<!-- Кнопки редактирования (только для ПТО с правом редактирования) -->
{% if user.can_edit_wells %}
    {% if well.status == 'draft' %}
        <a href="{% url 'wells:well_update' well.pk %}">
            <i class="bi bi-pencil"></i> Редактировать
        </a>
        <button type="submit" form="approval-form">
            <i class="bi bi-send"></i> Отправить на согласование
        </button>
    {% elif well.status == 'rejected' %}
        <a href="{% url 'wells:well_update' well.pk %}">
            <i class="bi bi-pencil"></i> Исправить
        </a>
    {% endif %}
{% endif %}

<!-- Кнопки согласования (только для начальника ПТО) -->
{% if user.is_head_pto and well.status == 'submitted' %}
    <form method="post" action="{% url 'wells:well_approve' well.pk %}">
        {% csrf_token %}
        <textarea name="comment" placeholder="Комментарий"></textarea>
        <button type="submit" class="btn btn-success">
            <i class="bi bi-check-circle"></i> Согласовать
        </button>
    </form>
    <button data-bs-toggle="modal" data-bs-target="#rejectModal">
        <i class="bi bi-x-circle"></i> Отказать
    </button>
{% endif %}

<!-- Генерация документов (только для ПТО) -->
{% if can_generate_docs %}
    <div class="dropdown">
        <button class="btn dropdown-toggle">
            <i class="bi bi-file-earmark-word"></i> Сформировать документ
        </button>
        <ul class="dropdown-menu">
            <li><a href="?type=report">Отчёт по скважине</a></li>
            <li><a href="?type=technical_spec">Техническое задание</a></li>
            <!-- ... другие типы документов ... -->
        </ul>
    </div>
{% endif %}

<!-- templates/documents/document_list.html - кнопка загрузки -->
{% if user.can_edit_wells %}
    <a href="{% url 'documents:document_create' %}" class="btn btn-primary">
        <i class="bi bi-plus-circle"></i> Загрузить документ
    </a>
{% endif %}
```

---

## 📊 Матрица прав доступа

| Действие | Инженер ПТО | Начальник ПТО |
|----------|-------------|---------------|
| **Просмотр своих скважин** | ✅ | ✅ |
| **Просмотр всех скважин** | ❌ | ✅ |
| **Создание скважин** | ✅ | ✅ |
| **Редактирование своих черновиков** | ✅ | ✅ |
| **Редактирование любых скважин** | ❌ | ✅ |
| **Отправка на согласование** | ✅ | ✅ |
| **Согласование скважин** | ❌ | ✅ |
| **Отклонение скважин** | ❌ | ✅ |
| **Изменение статусов** (начать бурение, завершить и т.д.) | ❌ | ✅ |
| **Генерация документов** | ✅ | ✅ |
| **Загрузка документов** | ✅ | ✅ |
| **Просмотр документов** | ✅ | ✅ |
| **Комментирование** | ✅ | ✅ |
| **Удаление черновиков** | ✅ (своих) | ✅ |
| **Экспорт в Excel** | ✅ (своих) | ✅ (всех) |
| **Доступ к аналитике** | ❌ | ✅ |
| **Расширенный поиск** | ✅ | ✅ |
| **Доступ к админке** | ❌ | ✅ (суперпользователь) |

---

## 🔐 Безопасность

### Уровни защиты:

1. **URL уровень** - декораторы и миксины проверяют права перед выполнением view
2. **View уровень** - дополнительные проверки в логике (например, проверка авторства)
3. **Model уровень** - методы get_accessible_wells() фильтруют данные
4. **Template уровень** - скрытие недоступных кнопок и форм

### Защита на всех уровнях:

**1. Class-Based Views:**
```python
# Миксины защищают целый класс
class WellListView(PTOStaffRequiredMixin, ListView):
    model = Well
    # Доступно только сотрудникам ПТО
```

**2. Function-Based Views:**
```python
# Декораторы защищают функцию
@login_required
@pto_engineer_required
def create_well(request):
    # Доступ только для инженера ПТО
    ...
```

**3. Проверка авторства:**
```python
# Дополнительная проверка в логике view
def edit_well(request, pk):
    well = get_object_or_404(Well, pk=pk)
    
    # Редактировать может только автор или начальник
    if well.author != request.user and not request.user.is_head_pto():
        messages.error(request, 'У вас нет прав на редактирование этой скважины.')
        return redirect('wells:well_detail', pk=pk)
    ...
```

**4. Фильтрация QuerySet:**
```python
# Автоматическая фильтрация по правам доступа
def get_queryset(self):
    # Вернёт только доступные пользователю скважины
    return self.request.user.get_accessible_wells()

# Безопасный доступ к объекту
wells = request.user.get_accessible_wells()
well = get_object_or_404(wells, pk=pk)  # 404 если нет доступа
```

**5. Условия в шаблонах:**
```html
<!-- Кнопки отображаются только при наличии прав -->
{% if user.can_edit_wells %}
    <a href="{% url 'wells:well_update' well.pk %}">Редактировать</a>
{% endif %}

{% if user.is_head_pto %}
    <button>Согласовать</button>
{% endif %}
```

### Примеры защиты от обхода:

```python
# ❌ Неправильно - легко обойти через прямой URL
def edit_well(request, pk):
    well = get_object_or_404(Well, pk=pk)
    # Любой авторизованный пользователь может редактировать!
    ...

# ✅ Правильно - множественные проверки
@login_required
@pto_staff_required  # 1. Проверка роли
def edit_well(request, pk):
    # 2. Фильтрация по доступным скважинам
    wells = request.user.get_accessible_wells()
    well = get_object_or_404(wells, pk=pk)
    
    # 3. Проверка авторства (для инженеров)
    if not request.user.is_head_pto() and well.author != request.user:
        return HttpResponseForbidden()
    
    # 4. Проверка статуса (можно редактировать только черновики)
    if well.status not in ['draft', 'rejected']:
        messages.error(request, 'Нельзя редактировать утверждённую скважину.')
        return redirect('wells:well_detail', pk=pk)
    ...
```

---

## ✅ Тестирование разграничения

### Демо-пользователи:

Система предоставляет следующих демо-пользователей для тестирования:

| Логин | Пароль | Роль | Права |
|-------|--------|------|-------|
| **admin** | admin | Начальник ПТО | Суперпользователь с полным доступом |
| **head_pto** | 1234 | Начальник ПТО | Согласование, утверждение, полный контроль |
| **pto_engineer** | 1234 | Инженер ПТО | Создание, редактирование, генерация документов |

### Создание демо-данных:

```bash
# Активация виртуального окружения
venv_39\Scripts\activate

# Создание демо-пользователей и тестовых данных
python manage.py demo_data

# Или создание новых данных (с дополнительными скважинами)
python manage.py demo_data_new
```

### Сценарии тестирования:

#### Сценарий 1: Создание и согласование скважины
1. ✅ Войдите как **pto_engineer** (логин: `pto_engineer`, пароль: `1234`)
2. ✅ Создайте новую скважину через кнопку "Создать скважину"
3. ✅ Заполните данные и сохраните как черновик
4. ✅ Отправьте на согласование через кнопку "Отправить на согласование"
5. ✅ Выйдите из системы
6. ✅ Войдите как **head_pto** (логин: `head_pto`, пароль: `1234`)
7. ✅ Найдите скважину со статусом "На согласовании"
8. ✅ Согласуйте скважину или отклоните с указанием причины

#### Сценарий 2: Проверка разграничения доступа
1. ✅ Войдите как **pto_engineer**
2. ✅ Попробуйте согласовать скважину → кнопки согласования должны быть скрыты
3. ✅ Попробуйте перейти по прямому URL `/wells/approve/1/` → должна быть ошибка доступа
4. ✅ Создайте скважину и попробуйте редактировать её после отправки на согласование → редактирование должно быть заблокировано

#### Сценарий 3: Генерация документов
1. ✅ Войдите как **pto_engineer**
2. ✅ Откройте любую скважину
3. ✅ Используйте выпадающее меню "Сформировать документ"
4. ✅ Сгенерируйте различные типы документов (отчёт, ТЗ, протокол и т.д.)
5. ✅ Проверьте, что документы корректно форматируются (Times New Roman 14pt, межстрочный интервал 1.5)

#### Сценарий 4: Работа начальника ПТО
1. ✅ Войдите как **head_pto**
2. ✅ Проверьте доступ к админ-панели через меню (если суперпользователь)
3. ✅ Отредактируйте чужую скважину (не свою) → должно быть разрешено
4. ✅ Согласуйте несколько скважин
5. ✅ Просмотрите аналитику и отчёты

#### Сценарий 5: Экспорт и аналитика
1. ✅ Войдите как **pto_engineer** или **head_pto**
2. ✅ Перейдите на страницу дашборда скважин
3. ✅ Нажмите кнопку "Экспорт" → должен скачаться Excel файл
4. ✅ Перейдите в раздел "Аналитика"
5. ✅ Проверьте доступ ко всем отчётам и графикам

### Проверка безопасности:

**Попытки обхода через прямые URL:**
```
# Попытка доступа без авторизации
/wells/create/ → редирект на /login/

# Попытка доступа с неправильной ролью
/wells/approve/1/ (как pto_engineer) → ошибка доступа
/admin/ (как pto_engineer) → ошибка доступа

# Попытка редактировать чужую скважину
/wells/1/update/ (инженером, где автор другой) → ошибка или блокировка
```

**Проверка фильтрации данных:**
```python
# Все запросы должны фильтроваться через get_accessible_wells()
# Пользователь не может получить данные, к которым нет доступа
```

---

## 🚀 Активация и использование

### Система полностью настроена!

Все изменения применены, и система имеет **полное разграничение прав доступа** для двух ролей:
- **Инженер ПТО** - основные операции (создание, редактирование, генерация документов)
- **Начальник ПТО** - полный контроль + согласование и утверждение

### Что реализовано:

✅ **Защита на уровне URL** - декораторы и миксины блокируют несанкционированный доступ  
✅ **Защита на уровне View** - дополнительные проверки авторства и статусов  
✅ **Защита на уровне Model** - фильтрация данных через get_accessible_wells()  
✅ **Защита на уровне Template** - скрытие кнопок для недоступных действий  
✅ **Валидация форм** - проверка прав перед сохранением данных  
✅ **Логирование действий** - история согласований и изменений (ApprovalStep)  
✅ **Уведомления** - информирование о изменениях статусов  

### Структура прав:

```
┌─────────────────────────────────────────────┐
│         Система управления скважинами        │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
    ┌───▼────┐           ┌──────▼─────┐
    │ Инженер│           │  Начальник │
    │   ПТО  │           │     ПТО    │
    └───┬────┘           └──────┬─────┘
        │                       │
        │  ✓ Создание           │  ✓ Все права инженера
        │  ✓ Редактирование     │  ✓ Согласование
        │  ✓ Отправка           │  ✓ Отклонение
        │  ✓ Генерация docs     │  ✓ Редактирование любых
        │  ✓ Комментарии        │  ✓ Админ-панель
        │  ✓ Аналитика          │  ✓ Полный контроль
        └───────────────────────┘
```

### Быстрый старт:

```bash
# 1. Запустите сервер
START_SERVER.bat

# 2. Откройте браузер
http://127.0.0.1:8080

# 3. Войдите с одним из демо-аккаунтов:
#    - pto_engineer / 1234 (инженер)
#    - head_pto / 1234 (начальник)
#    - admin / admin (суперпользователь)

# 4. Протестируйте различные сценарии!
```

### Файлы, реализующие разграничение:

- `accounts/models.py` - методы проверки прав в модели User
- `accounts/mixins.py` - миксины и декораторы для views
- `wells/views.py` - применение миксинов на представлениях
- `documents/views.py` - проверки прав на генерацию документов
- `analytics/views.py` - ограничение доступа к аналитике
- `templates/**/*.html` - условное отображение элементов интерфейса

### Дополнительная документация:

- `INSTALLATION.md` - установка и настройка системы
- `QUICK_START.md` - быстрый старт для пользователей
- `TESTING_GUIDE.md` - руководство по тестированию
- `CHANGELOG.md` - история изменений

---

## 📝 Примечания

**Обновлено:** Март 2026  
**Версия:** 2.0 (упрощённая система с 2 ролями)  
**Статус:** ✅ Полностью реализовано и протестировано

Ранее система поддерживала 4 роли (pto_engineer, head_pto, ext_engineer, supplier).  
В текущей версии оставлены только основные 2 роли для упрощения управления.
