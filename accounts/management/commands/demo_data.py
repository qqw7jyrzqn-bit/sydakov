"""
Команда для создания демонстрационных данных.
Создаёт пользователей с разными ролями и тестовые скважины.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wells.models import Well, ApprovalStep
from documents.models import Document
from notifications.models import Notification

User = get_user_model()


class Command(BaseCommand):
    help = 'Создание демонстрационных данных для системы ПТО'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начало создания демо-данных...'))
        
        # Создание пользователей
        self.stdout.write('Создание пользователей...')
        
        # 1. Суперпользователь (admin)
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Администратор',
                'last_name': 'Системы',
                'role': 'head_pto',
                'is_staff': True,
                'is_superuser': True,
                'phone': '+7 (999) 123-45-67',
                'company': 'ОАО "НефтьГазПром"',
            }
        )
        if created:
            admin.set_password('admin')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создан admin (пароль: admin)'))
        
        # 2. Инженер ПТО
        pto_engineer, created = User.objects.get_or_create(
            username='pto_engineer',
            defaults={
                'email': 'engineer@example.com',
                'first_name': 'Иван',
                'last_name': 'Петров',
                'role': 'pto_engineer',
                'is_staff': False,
                'phone': '+7 (999) 111-22-33',
                'company': 'ОАО "НефтьГазПром"',
            }
        )
        if created:
            pto_engineer.set_password('1234')
            pto_engineer.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создан pto_engineer (пароль: 1234)'))
        
        # 3. Начальник ПТО
        head_pto, created = User.objects.get_or_create(
            username='head_pto',
            defaults={
                'email': 'head@example.com',
                'first_name': 'Сергей',
                'last_name': 'Иванов',
                'role': 'head_pto',
                'is_staff': True,
                'phone': '+7 (999) 444-55-66',
                'company': 'ОАО "НефтьГазПром"',
            }
        )
        if created:
            head_pto.set_password('1234')
            head_pto.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создан head_pto (пароль: 1234)'))
        
        # 4. Поставщик
        supplier, created = User.objects.get_or_create(
            username='supplier',
            defaults={
                'email': 'supplier@example.com',
                'first_name': 'Дмитрий',
                'last_name': 'Козлов',
                'role': 'supplier',
                'is_staff': False,
                'phone': '+7 (999) 000-11-22',
                'company': 'ООО "БурСервис"',
            }
        )
        if created:
            supplier.set_password('1234')
            supplier.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создан supplier (пароль: 1234)'))
        
        # Создание скважин
        self.stdout.write('\nСоздание скважин...')
        
        # Скважина 1 - Черновик
        well1, created = Well.objects.get_or_create(
            name='Скважина №101-А',
            defaults={
                'field': 'Самотлорское месторождение',
                'coordinates': '61°05\'N 76°45\'E',
                'depth': 3500.00,
                'status': 'draft',
                'author': pto_engineer,
                'description': 'Разведочная скважина на нефть. Проектная глубина 3500 метров. Планируемое начало бурения - второй квартал 2026 года.',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создана {well1.name} (Черновик)'))
        
        # Скважина 2 - На согласовании
        well2, created = Well.objects.get_or_create(
            name='Скважина №102-Б',
            defaults={
                'field': 'Приобское месторождение',
                'coordinates': '61°35\'N 73°10\'E',
                'depth': 4200.00,
                'status': 'submitted',
                'author': pto_engineer,
                'description': 'Эксплуатационная скважина. Горизонтальное бурение на глубине 4000-4200 м.',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создана {well2.name} (На согласовании)'))
            
            # Создаём уведомление для начальника ПТО
            Notification.objects.create(
                recipient=head_pto,
                text=f'Скважина "{well2.name}" отправлена на согласование.',
                well=well2
            )
        
        # Скважина 3 - В работе
        well3, created = Well.objects.get_or_create(
            name='Скважина №103-В',
            defaults={
                'field': 'Русское месторождение',
                'coordinates': '62°15\'N 73°45\'E',
                'depth': 3800.00,
                'status': 'in_work',
                'author': pto_engineer,
                'description': 'Добывающая скважина. Бурение началось 15.01.2026. Текущая глубина: 2100 м.',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создана {well3.name} (В работе)'))
            
            # Создаём шаги согласования
            ApprovalStep.objects.create(
                well=well3,
                user=head_pto,
                status='approved',
                comment='Проект согласован. Можно начинать бурение.'
            )
        
        # Создание документов
        self.stdout.write('\nСоздание документов...')
        
        doc1, created = Document.objects.get_or_create(
            well=well2,
            title='Техническое задание на бурение',
            defaults={
                'document_type': 'technical_spec',
                'uploaded_by': pto_engineer,
                'description': 'Техническое задание на бурение скважины №102-Б',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создан документ: {doc1.title}'))
        
        doc2, created = Document.objects.get_or_create(
            well=well3,
            title='Промежуточный отчёт о бурении',
            defaults={
                'document_type': 'report',
                'uploaded_by': pto_engineer,
                'description': 'Отчёт о ходе бурения на 15.01.2026',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создан документ: {doc2.title}'))
        
        # Создание уведомлений
        self.stdout.write('\nСоздание уведомлений...')
        
        notif1, created = Notification.objects.get_or_create(
            recipient=pto_engineer,
            text='Добро пожаловать в систему инженера ПТО!',
            defaults={'read': False}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создано уведомление для инженера'))
        
        notif2, created = Notification.objects.get_or_create(
            recipient=head_pto,
            text=f'Требуется согласование скважины "{well2.name}"',
            defaults={'read': False, 'well': well2}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создано уведомление для начальника'))
        
        # Итоги
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✓ Демо-данные успешно созданы!'))
        self.stdout.write('\n' + 'Учётные записи для входа:')
        self.stdout.write(f'  Админ:           admin / admin')
        self.stdout.write(f'  Инженер ПТО:     pto_engineer / 1234')
        self.stdout.write(f'  Начальник ПТО:   head_pto / 1234')
        self.stdout.write('='*60)
