from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Article, Category, ArticleImage
from .forms import ArticleForm, ModerationForm, RegistrationForm, ArticleImageForm

from django.contrib.auth.models import User


def is_moderator(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def home(request):
    published_articles = Article.objects.filter(status="published")[:5]
    categories = Category.objects.all()

    return render(
        request,
        "articles/home.html",
        {
            "recent_articles": published_articles,
            "categories": categories,
        },
    )


def article_list(request):
    articles = Article.objects.filter(status="published")

    category_id = request.GET.get("category")
    if category_id:
        articles = articles.filter(category_id=category_id)

    paginator = Paginator(articles, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    categories = Category.objects.all()

    return render(
        request,
        "articles/articlelist.html",
        {
            "articles": page_obj,
            "categories": categories,
            "selected_category": int(category_id) if category_id else None,
        },
    )


def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, status="published")
    article.increment_views()
    return render(request, "articles/articledetail.html", {"article": article})


@login_required
def create_article(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.status = "pending"
            article.save()

            files = request.FILES.getlist("image")
            for f in files:
                if f:
                    ArticleImage.objects.create(
                        article=article,
                        image=f,
                        caption=request.POST.get("caption", ""),
                    )

            messages.success(
                request, f'Статья "{article.title}" успешно отправлена на модерацию!'
            )
            return redirect(
                "articles:article_detail", pk=article.pk
            )
    else:
        form = ArticleForm()

    return render(
        request,
        "articles/createarticle.html",
        {
            "form": form,
            "categories": Category.objects.all(),
        },
    )

@login_required
def edit_article(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.status = "pending"
            article.moderator = None
            article.moderation_comment = ""
            article.save()

            messages.success(
                request,
                "Статья успешно отредактирована и отправлена на повторную модерацию.",
            )
            return redirect("articles:home.html", pk=article.pk)
    else:
        form = ArticleForm(instance=article)

    return render(
        request, "articles/editarticle.html", {"form": form, "article": article}
    )


@login_required
@user_passes_test(is_moderator)
def moderation_queue(request):
    pending_articles = Article.objects.filter(status="pending").order_by("-created_at")

    if request.method == "POST":
        article_id = request.POST.get("article_id")
        article = get_object_or_404(Article, pk=article_id)
        form = ModerationForm(request.POST)

        if form.is_valid():
            action = form.cleaned_data["action"]
            comment = form.cleaned_data.get("comment", "")

            if action == "approve":
                article.publish()
                article.moderator = request.user
                article.save()
                messages.success(
                    request, f'Статья "{article.title}" одобрена и опубликована.'
                )
            else:
                article.reject(comment)
                article.moderator = request.user
                article.save()
                messages.success(
                    request,
                    f'Статья "{article.title}" отклонена. Причина отправлена автору.',
                )

            return redirect("articles:moderation_queue")
        else:
            messages.error(request, "Ошибка в форме модерации.")

    else:
        form = ModerationForm()

    return render(
        request,
        "articles/moderationqueue.html",
        {
            "articles": pending_articles,
            "form": form,
        },
    )


def register(request):
    if request.user.is_authenticated:
        return redirect("articles:home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            return redirect("articles:home")
    else:
        form = RegistrationForm()

    return render(request, "articles/registration/register.html", {"form": form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("articles:home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f"С возвращением, {user.username}!")
            return redirect("articles:home")
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")

    return render(request, "articles/registration/login.html")


def user_logout(request):
    logout(request)
    messages.info(request, "Вы успешно вышли из системы.")
    return redirect("articles:home")


@login_required
def user_notifications(request):
    user_articles = Article.objects.filter(author=request.user).order_by("-created_at")

    context = {
        "user_articles": user_articles,
    }
    return render(request, "articles/notifications.html", context)