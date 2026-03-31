from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField("Название категории", max_length=100)
    description = models.TextField("Описание", blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Article(models.Model):
    STATUS_CHOICES = [
        ("draft", "Черновик"),
        ("pending", "На модерации"),
        ("published", "Опубликовано"),
        ("rejected", "Отклонено"),
    ]

    title = models.CharField("Заголовок", max_length=200)
    content = models.TextField("Содержание")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Категория",
        related_name="articles",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор", related_name="articles"
    )
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)
    published_at = models.DateTimeField("Опубликовано", null=True, blank=True)
    moderation_comment = models.TextField("Комментарий модератора", blank=True)
    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Модератор",
        related_name="moderated_articles",
    )
    views_count = models.PositiveIntegerField("Просмотры", default=0)

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def publish(self):
        self.status = "published"
        self.published_at = timezone.now()
        self.save()

    def reject(self, comment):
        self.status = "rejected"
        self.moderation_comment = comment
        self.save()

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=["views_count"])
