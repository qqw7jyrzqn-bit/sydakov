"""
Тесты для приложения wells.
"""
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from wells.models import Well, ApprovalStep


class WellModelTest(TestCase):
    """Тесты модели Well"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            role='pto_engineer'
        )
        
        self.well = Well.objects.create(
            name='Тестовая скважина',
            field='Тестовое месторождение',
            coordinates='60°N 70°E',
            depth=3000.00,
            status='draft',
            author=self.user,
            description='Тестовое описание'
        )
    
    def test_well_creation(self):
        """Тест создания скважины"""
        self.assertEqual(self.well.name, 'Тестовая скважина')
        self.assertEqual(self.well.status, 'draft')
        self.assertEqual(self.well.author, self.user)
    
    def test_send_for_approval(self):
        """Тест отправки на согласование"""
        result = self.well.send_for_approval(self.user)
        self.assertTrue(result)
        self.assertEqual(self.well.status, 'submitted')
    
    def test_well_str(self):
        """Тест строкового представления"""
        expected = f"{self.well.name} (Черновик)"
        self.assertEqual(str(self.well), expected)


class WellViewsTest(TestCase):
    """Тесты views для скважин"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            role='pto_engineer'
        )
        self.client.login(username='testuser', password='testpass')
    
    def test_dashboard_view(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Дашборд')
    
    def test_well_list_view(self):
        """Тест списка скважин"""
        response = self.client.get(reverse('wells:well_list'))
        self.assertEqual(response.status_code, 200)


class UserModelTest(TestCase):
    """Тесты модели User"""
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass',
            role='pto_engineer',
            first_name='Иван',
            last_name='Тестов'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'pto_engineer')
        self.assertTrue(user.is_pto_engineer())
        self.assertTrue(user.can_edit_wells())
    
    def test_head_pto_permissions(self):
        """Тест прав начальника ПТО"""
        user = User.objects.create_user(
            username='headuser',
            password='testpass',
            role='head_pto'
        )
        
        self.assertTrue(user.is_head_pto())
        self.assertTrue(user.can_approve_wells())
        self.assertTrue(user.can_edit_wells())
