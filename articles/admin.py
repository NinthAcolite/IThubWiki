from django.contrib import admin
from .models import Category, Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]
    list_per_page = 20


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "status", "created_at", "moderator"]
    list_filter = ["status", "created_at", "category"]
    search_fields = ["title", "author__username", "moderation_comment"]
    readonly_fields = ["created_at", "updated_at", "published_at"]
    list_per_page = 20

    fieldsets = (
        ("Основная информация", {"fields": ("title", "content", "category", "author")}),
        (
            "Статус и модерация",
            {"fields": ("status", "moderator", "moderation_comment")},
        ),
        ("Даты", {"fields": ("created_at", "updated_at", "published_at")}),
    )

    actions = ["approve_articles", "reject_articles"]

    def approve_articles(self, request, queryset):
        count = 0
        for article in queryset:
            if article.status == "pending":
                article.publish()
                article.moderator = request.user
                article.save()
                count += 1
        self.message_user(request, f"Одобрено {count} статей")

    approve_articles.short_description = "Одобрить выбранные статьи"

    def reject_articles(self, request, queryset):
        count = 0
        for article in queryset:
            if article.status == "pending":
                article.status = "rejected"
                article.moderator = request.user
                article.save()
                count += 1
        self.message_user(request, f"Отклонено {count} статей")

    reject_articles.short_description = "Отклонить выбранные статьи"
