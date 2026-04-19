from django import template
from django.utils.safestring import mark_safe
from ..models import Article, ArticleImage
import re

register = template.Library()


@register.filter(name="wikilinks")
def wikilinks(value):
    if not value:
        return value

    def replace_link(match):
        text = match.group(1).strip()

        if text.lower().startswith("image:"):
            filename = text[6:].strip()

            image = ArticleImage.objects.filter(image__endswith=filename).first()

            if image and image.image:
                img_url = image.image.url
                return f'''
                    <img src="{img_url}" 
                         class="img-fluid rounded my-3 shadow-sm" 
                         alt="{filename}" 
                         style="max-width: 100%; height: auto;">
                '''
            else:
                return f'<p style="color:red;">[Изображение {filename} не найдено]</p>'

        try:
            article = Article.objects.get(title__iexact=text, status="published")
            url = f"/article/{article.pk}/"
            return f'<a href="{url}" class="wiki-link" style="color: #007bff; font-weight: 500;">{text}</a>'
        except Article.DoesNotExist:
            return f'<span style="color:#999; text-decoration: underline dashed;">{text}</span>'

    result = re.sub(r"\[\[(.+?)\]\]", replace_link, value)
    return mark_safe(result)
