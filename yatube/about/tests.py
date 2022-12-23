from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self):
        # Создаём экземпляр клиента.
        self.guest_client = Client()

    def test_static_pages(self):
        """Тест доступности статических страниц"""
        response = self.guest_client.get('/about/author/')
        self.assertEquals(response.reason_phrase, 'OK')
        response = self.guest_client.get('/about/tech/')
        self.assertEquals(response.reason_phrase, 'OK')

    def test_templates_static_pages(self):
        """Тест шаблонов статических страниц"""
        response = self.guest_client.get('/about/author/')
        self.assertTemplateUsed(response, 'about/author.html')
        response = self.guest_client.get('/about/tech/')
        self.assertTemplateUsed(response, 'about/tech.html')
