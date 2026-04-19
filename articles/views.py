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
    total_articles = Article.objects.filter(status="published").count()

    context = {
        "recent_articles": published_articles,
        "categories": categories,
        "total_articles": total_articles,
    }
    return render(request, "articles/home.html", context)


def article_list(request):
    articles = Article.objects.filter(status="published")
    paginator = Paginator(articles, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "articles/articlelist.html", {"articles": page_obj})


def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, status="published")
    article.increment_views()
    return render(request, "articles/articledetail.html", {"article": article})


@login_required
def create_article(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        image_form = ArticleImageForm(request.POST, request.FILES)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.status = "pending"
            article.save()

            files = request.FILES.getlist("image")
            for f in files:
                ArticleImage.objects.create(
                    article=article, image=f, caption=request.POST.get("caption", "")
                )

            messages.success(
                request, f'Статья "{article.title}" успешно отправлена на модерацию!'
            )
            return redirect("articles:home")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме")
    else:
        form = ArticleForm()
        image_form = ArticleImageForm()

    categories = Category.objects.all()
    return render(
        request,
        "articles/createarticle.html",
        {
            "form": form,
            "categories": categories,
            # "image_form": image_form,
        },
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
                    request, f'Статья "{article.title}" одобрена и опубликована'
                )
            else:
                article.reject(comment)
                article.moderator = request.user
                article.save()
                messages.success(request, f'Статья "{article.title}" отклонена')

            return redirect("articles:moderation_queue")
        else:
            messages.error(request, "Пожалуйста, заполните форму корректно")
    else:
        form = ModerationForm()

    return render(
        request,
        "articles/moderationqueue.html",
        {"articles": pending_articles, "form": form},
    )


def register(request):
    if request.user.is_authenticated:
        return redirect("articles:home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = User.objects.create_user(username, email, password)
            login(request, user)
            messages.success(
                request, f"Добро пожаловать, {username}! Регистрация успешно завершена."
            )
            return redirect("articles:home")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме")
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

        if user is not None:
            login(request, user)
            messages.success(request, f"С возвращением, {username}!")
            next_url = request.GET.get("next", "articles:home")
            return redirect(next_url)
        else:
            messages.error(request, "Неверное имя пользователя или пароль")

    return render(request, "articles/registration/login.html")


def user_logout(request):
    logout(request)
    messages.info(request, "Вы успешно вышли из системы")
    return redirect("articles:home")
