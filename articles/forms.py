from django import forms
from .models import Article, Category


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "content", "category"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите заголовок статьи",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 15,
                    "placeholder": "Введите содержание статьи...",
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "title": "Заголовок статьи",
            "content": "Содержание",
            "category": "Категория",
        }


class ModerationForm(forms.Form):
    action = forms.ChoiceField(
        choices=[("approve", "Одобрить и опубликовать"), ("reject", "Отклонить")],
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label="Решение",
    )
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Укажите причину отклонения (если применимо)",
            }
        ),
        required=False,
        label="Комментарий модератора",
    )


class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Введите имя пользователя"}
        ),
        label="Имя пользователя",
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "example@ithub.spb.ru"}
        ),
        label="Email",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"}
        ),
        label="Пароль",
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Подтвердите пароль"}
        ),
        label="Подтверждение пароля",
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        from django.contrib.auth.models import User

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        from django.contrib.auth.models import User

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data
