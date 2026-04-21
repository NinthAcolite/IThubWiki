from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from articles.models import Category, Article


class ArticleTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.moderator = User.objects.create_user(
            username="moderator", password="password123", is_staff=True
        )

        self.category = Category.objects.create(
            name="Программирование", description="Раздел про код"
        )

        self.article = Article.objects.create(
            title="Тестовая статья",
            content="Это тестовая статья для автотестов.",
            author=self.user,
            category=self.category,
            status="published",
        )

    def test_user_can_register(self):
        response = self.client.post(
            reverse("articles:register"),
            {
                "username": "newuser123",
                "email": "newuser@example.com",
                "password": "testpass123",
                "password_confirm": "testpass123",
            },
        )
        self.assertEqual(
            response.status_code, 302
        )

    def test_user_can_login(self):
        response = self.client.post(
            reverse("articles:login"),
            {"username": "testuser", "password": "password123"},
        )
        self.assertEqual(response.status_code, 302)

    def test_user_can_create_article(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(
            reverse("articles:create_article"),
            {
                "title": "Новая тестовая статья",
                "content": "Содержимое новой статьи для теста.",
                "category": self.category.id,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Article.objects.filter(title="Новая тестовая статья").exists())

    def test_user_can_edit_article(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(
            reverse("articles:edit_article", args=[self.article.pk]),
            {
                "title": "Обновлённая тестовая статья",
                "content": "Новое содержание после редактирования.",
                "category": self.category.id,
            },
        )
        self.assertEqual(response.status_code, 302)

        self.article.refresh_from_db()
        self.assertEqual(
            self.article.status, "pending"
        )

    def test_article_detail_page(self):
        response = self.client.get(
            reverse("articles:article_detail", args=[self.article.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)

    def test_notifications_page(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("articles:notifications"))
        self.assertEqual(response.status_code, 200)
