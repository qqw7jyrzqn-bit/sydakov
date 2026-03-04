"""
Команда для создания расширенных демонстрационных данных.
Создаёт пользователей с разными ролями и множество тестовых скважин.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wells.models import Well, ApprovalStep
from documents.models import Document
from notifications.models import Notification

User = get_user_model()


class Command(BaseCommand):
    help = 'Создание расширенных демонстрационных данных для системы ПТО'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начало создания демо-данных...'))
        
        # Удаляем старые данные
        self.stdout.write('Очистка старых данных...')
        Well.objects.all().delete()
        Document.objects.all().delete()
        Notification.objects.all().delete()
        
        # Создание пользователей
        self.stdout.write('\nСоздание пользователей...')
        
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
        self.stdout.write(self.style.SUCCESS(f'  ✓ admin (пароль: admin)'))
        
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
        self.stdout.write(self.style.SUCCESS(f'  ✓ pto_engineer (пароль: 1234)'))
        
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
        self.stdout.write(self.style.SUCCESS(f'  ✓ head_pto (пароль: 1234)'))
        
        # Создание скважин
        self.stdout.write('\nСоздание скважин...')
        
        wells_data = [
            {
                'name': 'Скважина №101-А',
                'field': 'Самотлорское',
                'coordinates': '61°05\'N 76°45\'E',
                'depth': 2450.00,
                'status': 'approved',
                'description': 'Эксплуатационная скважина на северном участке месторождения.'
            },
            {
                'name': 'Скважина №102-Б',
                'field': 'Самотлорское',
                'coordinates': '61°08\'N 76°52\'E',
                'depth': 2680.00,
                'status': 'in_work',
                'description': 'Бурение в процессе, продуктивный пласт достигнут.'
            },
            {
                'name': 'Скважина №103-В',
                'field': 'Самотлорское',
                'coordinates': '61°12\'N 76°48\'E',
                'depth': 2320.00,
                'status': 'completed',
                'description': 'Скважина пробурена, проведены испытания пластов.'
            },
            {
                'name': 'Скважина №104-А',
                'field': 'Приобское',
                'coordinates': '61°35\'N 73°10\'E',
                'depth': 2890.00,
                'status': 'approved',
                'description': 'Наклонно-направленная скважина для разработки южного участка.'
            },
            {
                'name': 'Скважина №105-Б',
                'field': 'Приобское',
                'coordinates': '61°40\'N 73°15\'E',
                'depth': 3120.00,
                'status': 'submitted',
                'description': 'Проект подан на утверждение, ожидает решения комиссии.'
            },
            {
                'name': 'Скважина №106-В',
                'field': 'Приобское',
                'coordinates': '61°42\'N 73°20\'E',
                'depth': 2750.00,
                'status': 'in_work',
                'description': 'Ведутся буровые работы, пройдено 1850 метров.'
            },
            {
                'name': 'Скважина №107-А',
                'field': 'Ванкорское',
                'coordinates': '63°05\'N 87°45\'E',
                'depth': 3450.00,
                'status': 'approved',
                'description': 'Глубокая разведочная скважина на северном куполе.'
            },
            {
                'name': 'Скважина №108-Б',
                'field': 'Ванкорское',
                'coordinates': '63°10\'N 87°50\'E',
                'depth': 3280.00,
                'status': 'completed',
                'description': 'Бурение завершено, получен промышленный приток нефти.'
            },
            {
                'name': 'Скважина №109-В',
                'field': 'Ванкорское',
                'coordinates': '63°15\'N 87°55\'E',
                'depth': 3650.00,
                'status': 'draft',
                'description': 'Проект в разработке, проводятся дополнительные геологические исследования.'
            },
            {
                'name': 'Скважина №110-А',
                'field': 'Русское',
                'coordinates': '67°15\'N 75°10\'E',
                'depth': 2980.00,
                'status': 'approved',
                'description': 'Эксплуатационная скважина на центральном участке.'
            },
            {
                'name': 'Скважина №111-Б',
                'field': 'Русское',
                'coordinates': '67°20\'N 75°15\'E',
                'depth': 3150.00,
                'status': 'in_work',
                'description': 'Спущена эксплуатационная колонна, проводится цементирование.'
            },
            {
                'name': 'Скважина №112-В',
                'field': 'Русское',
                'coordinates': '67°25\'N 75°20\'E',
                'depth': 2850.00,
                'status': 'submitted',
                'description': 'Проектная документация на стадии согласования.'
            },
            {
                'name': 'Скважина №113-А',
                'field': 'Харьягинское',
                'coordinates': '65°30\'N 58°15\'E',
                'depth': 4120.00,
                'status': 'approved',
                'description': 'Глубокая разведочная скважина для оценки запасов.'
            },
            {
                'name': 'Скважина №114-Б',
                'field': 'Харьягинское',
                'coordinates': '65°35\'N 58°20\'E',
                'depth': 3890.00,
                'status': 'rejected',
                'description': 'Проект отклонён из-за несоответствия требованиям безопасности.'
            },
            {
                'name': 'Скважина №115-В',
                'field': 'Харьягинское',
                'coordinates': '65°40\'N 58°25\'E',
                'depth': 4250.00,
                'status': 'draft',
                'description': 'Разработка технического задания, подбор бурового оборудования.'
            },
            {
                'name': 'Скважина №116-А',
                'field': 'Уренгойское',
                'coordinates': '66°10\'N 76°50\'E',
                'depth': 3560.00,
                'status': 'approved',
                'description': 'Горизонтальная скважина для разработки газоконденсатных залежей.'
            },
            {
                'name': 'Скважина №117-Б',
                'field': 'Уренгойское',
                'coordinates': '66°15\'N 76°55\'E',
                'depth': 3720.00,
                'status': 'in_work',
                'description': 'Проводится зарезка бокового ствола, азимут 125°.'
            },
            {
                'name': 'Скважина №118-В',
                'field': 'Уренгойское',
                'coordinates': '66°20\'N 77°00\'E',
                'depth': 3480.00,
                'status': 'completed',
                'description': 'Строительство завершено, скважина готова к вводу в эксплуатацию.'
            },
            {
                'name': 'Скважина №119-А',
                'field': 'Ямбургское',
                'coordinates': '67°55\'N 75°30\'E',
                'depth': 3990.00,
                'status': 'approved',
                'description': 'Многоствольная скважина для увеличения нефтеотдачи.'
            },
            {
                'name': 'Скважина №120-Б',
                'field': 'Ямбургское',
                'coordinates': '68°00\'N 75°35\'E',
                'depth': 4180.00,
                'status': 'submitted',
                'description': 'Проект новой разведочной скважины на восточном участке.'
            },
        ]
        
        wells = []
        for well_data in wells_data:
            well = Well.objects.create(
                name=well_data['name'],
                field=well_data['field'],
                coordinates=well_data['coordinates'],
                depth=well_data['depth'],
                status=well_data['status'],
                description=well_data['description'],
                author=pto_engineer,
            )
            wells.append(well)
            self.stdout.write(self.style.SUCCESS(f'  ✓ {well.name}'))
        
        # Создание документов
        self.stdout.write('\nСоздание документов...')
        
        docs_data = [
            {
                'well': wells[0],  # №101-А
                'title': 'Технический отчёт по бурению',
                'document_type': 'report',
                'description': 'Детальный технический отчёт по результатам бурения скважины.'
            },
            {
                'well': wells[0],
                'title': 'Геологическое заключение',
                'document_type': 'geology_report',
                'description': 'Результаты геологических исследований продуктивных пластов.'
            },
            {
                'well': wells[1],  # №102-Б
                'title': 'Программа проводки скважины',
                'document_type': 'drilling_program',
                'description': 'Утверждённая программа бурения с режимами и материалами.'
            },
            {
                'well': wells[1],
                'title': 'План безопасности',
                'document_type': 'safety_plan',
                'description': 'Мероприятия по обеспечению промышленной безопасности.'
            },
            {
                'well': wells[2],  # №103-В
                'title': 'Акт о завершении строительства',
                'document_type': 'completion_report',
                'description': 'Приёмка скважины комиссией после завершения работ.'
            },
            {
                'well': wells[2],
                'title': 'Протокол испытаний',
                'document_type': 'protocol',
                'description': 'Результаты гидродинамических исследований скважины.'
            },
            {
                'well': wells[3],  # №104-А
                'title': 'Техническое задание на бурение',
                'document_type': 'technical_spec',
                'description': 'Исходные данные и требования к проектированию скважины.'
            },
            {
                'well': wells[4],  # №105-Б
                'title': 'Геологический прогноз',
                'document_type': 'geology_report',
                'description': 'Прогнозный геологический разрез по данным сейсморазведки.'
            },
            {
                'well': wells[5],  # №106-В
                'title': 'Отчёт о ходе работ',
                'document_type': 'report',
                'description': 'Промежуточный отчёт о выполнении буровых работ.'
            },
            {
                'well': wells[6],  # №107-А
                'title': 'Программа исследований',
                'document_type': 'drilling_program',
                'description': 'План геофизических и гидродинамических исследований.'
            },
            {
                'well': wells[7],  # №108-Б
                'title': 'Протокол опытно-промышленных испытаний',
                'document_type': 'protocol',
                'description': 'Результаты опробования продуктивных горизонтов.'
            },
            {
                'well': wells[8],  # №109-В
                'title': 'Технико-экономическое обоснование',
                'document_type': 'technical_spec',
                'description': 'Обоснование экономической целесообразности бурения.'
            },
            {
                'well': wells[9],  # №110-А
                'title': 'План производства работ',
                'document_type': 'safety_plan',
                'description': 'График и мероприятия по охране труда.'
            },
            {
                'well': wells[10],  # №111-Б
                'title': 'Акт приёмки цементажа',
                'document_type': 'completion_report',
                'description': 'Результаты проверки качества цементирования колонн.'
            },
            {
                'well': wells[12],  # №113-А
                'title': 'Сводный геологический отчёт',
                'document_type': 'geology_report',
                'description': 'Комплексный анализ геологического строения месторождения.'
            },
            {
                'well': wells[15],  # №116-А
                'title': 'Программа горизонтального бурения',
                'document_type': 'drilling_program',
                'description': 'Технология проводки горизонтального участка ствола.'
            },
            {
                'well': wells[17],  # №118-В
                'title': 'Итоговый отчёт по скважине',
                'document_type': 'report',
                'description': 'Полный комплект документации по завершённой скважине.'
            },
        ]
        
        for doc_data in docs_data:
            doc = Document.objects.create(
                well=doc_data['well'],
                title=doc_data['title'],
                document_type=doc_data['document_type'],
                description=doc_data['description'],
                uploaded_by=pto_engineer
            )
            self.stdout.write(self.style.SUCCESS(f'  ✓ {doc.title}'))
        
        # Создание уведомлений
        self.stdout.write('\nСоздание уведомлений...')
        
        Notification.objects.create(
            recipient=head_pto,
            text=f'Скважина "{wells[4].name}" отправлена на согласование.',
            well=wells[4]
        )
        
        Notification.objects.create(
            recipient=head_pto,
            text=f'Скважина "{wells[11].name}" отправлена на согласование.',
            well=wells[11]
        )
        
        Notification.objects.create(
            recipient=head_pto,
            text=f'Скважина "{wells[19].name}" отправлена на согласование.',
            well=wells[19]
        )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Создано уведомлений: 3'))
        
        # Создание шагов согласования
        self.stdout.write('\nСоздание шагов согласования...')
        
        # Для утверждённых скважин
        for well in [wells[0], wells[3], wells[6], wells[9], wells[12], wells[15], wells[18]]:
            ApprovalStep.objects.create(
                well=well,
                user=head_pto,
                status='approved',
                comment='Проект согласован. Можно начинать работы.'
            )
        
        # Для отклонённой скважины
        ApprovalStep.objects.create(
            well=wells[13],
            user=head_pto,
            status='rejected',
            comment='Не выполнены требования промышленной безопасности. Требуется доработка.'
        )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Создано шагов: 8'))
        
        # Итоги
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✓ Расширенные демо-данные успешно созданы!'))
        self.stdout.write('\n' + 'Статистика:')
        self.stdout.write(f'  Скважин:   {len(wells)}')
        self.stdout.write(f'  Документов: {len(docs_data)}')
        self.stdout.write(f'  Уведомлений: 3')
        self.stdout.write('\n' + 'Учётные записи для входа:')
        self.stdout.write(f'  Админ:           admin / admin')
        self.stdout.write(f'  Инженер ПТО:     pto_engineer / 1234')
        self.stdout.write(f'  Начальник ПТО:   head_pto / 1234')
        self.stdout.write('='*70)
