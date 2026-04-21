from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.home, name="home"),
    path("articles/", views.article_list, name="article_list"),
    path("article/<int:pk>/", views.article_detail, name="article_detail"),
    path("article/<int:pk>/edit/", views.edit_article, name="edit_article"),
    path("create/", views.create_article, name="create_article"),
    path("moderation/", views.moderation_queue, name="moderation_queue"),
    path("notifications/", views.user_notifications, name="notifications"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
]
