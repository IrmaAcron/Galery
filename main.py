import os
import sys
import django
from django.conf import settings
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
from django.db import models
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static
from django.apps import AppConfig
from decimal import Decimal

# Конфигурация приложения gallery
class GalleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gallery'

# Настройка Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
settings.configure(
    BASE_DIR=BASE_DIR,
    SECRET_KEY='your-secret-key-here',  # Замените на свой секретный ключ
    DEBUG=True,
    ALLOWED_HOSTS=['*'],
    INSTALLED_APPS=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'gallery',
    ],
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ],
    ROOT_URLCONF='__main__',
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    },
    LANGUAGE_CODE='ru-ru',
    TIME_ZONE='UTC',
    USE_I18N=True,
    USE_TZ=True,
    STATIC_URL='/static/',
    STATICFILES_DIRS=[os.path.join(BASE_DIR, 'static')],
    MEDIA_URL='/media/',
    MEDIA_ROOT=os.path.join(BASE_DIR, 'media'),
    DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
)

django.setup()

# Модель для картин
class Painting(models.Model):
    CURRENCY_CHOICES = [
        ('TON', 'Toncoin (TON)'),
        ('ETH', 'Ethereum (ETH)'),
        ('USD', 'US Dollar (USD)'),
    ]
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to='paintings/', verbose_name="Изображение")
    price = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True, verbose_name="Цена")
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='TON', verbose_name="Валюта")
    is_auction = models.BooleanField(default=False, verbose_name="На аукционе")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return self.title

    def price_in_eur(self):
        if not self.price:
            return None
        rates = {
            'TON': Decimal('5.50'),
            'ETH': Decimal('2500'),
            'USD': Decimal('0.92'),
        }
        return round(self.price * rates[self.currency], 2)

    class Meta:
        app_label = 'gallery'
        verbose_name = "Картина"
        verbose_name_plural = "Картины"

admin.site.register(Painting)

# Форма для добавления/редактирования картины
class PaintingForm(forms.ModelForm):
    class Meta:
        model = Painting
        fields = ['title', 'description', 'image', 'price', 'currency', 'is_auction']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

# Представления
def gallery_list(request):
    paintings = Painting.objects.all().order_by('-created_at')
    return render(request, 'gallery_list.html', {'paintings': paintings})

def add_painting(request):
    if request.method == 'POST':
        form = PaintingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gallery_list')
    else:
        form = PaintingForm()
    return render(request, 'add_painting.html', {'form': form})

def edit_painting(request, painting_id):
    painting = get_object_or_404(Painting, id=painting_id)
    if request.method == 'POST':
        form = PaintingForm(request.POST, request.FILES, instance=painting)
        if form.is_valid():
            form.save()
            return redirect('gallery_list')
    else:
        form = PaintingForm(instance=painting)
    return render(request, 'edit_painting.html', {'form': form, 'painting': painting})

# URL-ы
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', gallery_list, name='gallery_list'),
    path('add/', add_painting, name='add_painting'),
    path('edit/<int:painting_id>/', edit_painting, name='edit_painting'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Шаблоны
base_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Галерея картин</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Roboto', sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        header {
            background: #2c3e50;
            color: #fff;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        header h1 {
            font-family: 'Playfair Display', serif;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        header a {
            color: #fff;
            text-decoration: none;
            font-weight: 700;
            padding: 10px 20px;
            background: #3498db;
            border-radius: 5px;
            transition: background 0.3s;
        }
        header a:hover {
            background: #2980b9;
        }
        main {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }
        .painting {
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            padding: 20px;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .painting:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.15);
        }
        .image-container {
            position: relative;
            width: 100%;
            margin-bottom: 15px;
        }
        .protected-image {
            width: 100%;
            height: auto;
            border-radius: 8px;
            display: block;
        }
        .overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: transparent;
        }
        h2 {
            font-family: 'Playfair Display', serif;
            font-size: 1.5em;
            margin-bottom: 10px;
            color: #2c3e50;
        }
        p {
            font-size: 1em;
            margin-bottom: 10px;
        }
        .button {
            display: inline-block;
            padding: 8px 16px;
            background: #e74c3c;
            color: #fff;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s;
        }
        .button:hover {
            background: #c0392b;
        }
        form {
            background: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto;
        }
        form h2 {
            margin-bottom: 20px;
        }
        form label {
            display: block;
            margin: 10px 0 5px;
            font-weight: 700;
        }
        form input, form textarea, form select {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
        }
        form button {
            background: #2ecc71;
            color: #fff;
            border: none;
            padding: 12px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.3s;
        }
        form button:hover {
            background: #27ae60;
        }
    </style>
</head>
<body>
    <header>
        <h1>Галерея картин</h1>
        <a href="{% url 'add_painting' %}">Добавить картину</a>
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
    <script>
        document.addEventListener('contextmenu', function(e) {
            if (e.target.tagName === 'IMG') e.preventDefault();
        });
        document.addEventListener('dragstart', function(e) {
            if (e.target.tagName === 'IMG') e.preventDefault();
        });
    </script>
</body>
</html>
"""

gallery_list_html = """
{% extends 'base.html' %}
{% load static %}

{% block content %}
    <div class="gallery">
        {% for painting in paintings %}
            <div class="painting">
                <div class="image-container">
                    <img src="{{ painting.image.url }}" alt="{{ painting.title }}" class="protected-image">
                    <div class="overlay"></div>
                </div>
                <h2>{{ painting.title }}</h2>
                <p>{{ painting.description }}</p>
                {% if painting.price %}
                    <p>Цена: {{ painting.price_in_eur }} € ({{ painting.price }} {{ painting.currency }})</p>
                {% endif %}
                <p>Статус: {% if painting.is_auction %}На аукционе{% else %}Продажа{% endif %}</p>
                <a href="{% url 'edit_painting' painting.id %}" class="button">Редактировать</a>
            </div>
        {% endfor %}
    </div>
{% endblock %}
"""

add_painting_html = """
{% extends 'base.html' %}

{% block content %}
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        <h2>Добавить картину</h2>
        {{ form.as_p }}
        <p><small>Укажите цену в выбранной валюте (будет конвертировано в евро)</small></p>
        <button type="submit">Добавить</button>
    </form>
{% endblock %}
"""

edit_painting_html = """
{% extends 'base.html' %}

{% block content %}
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        <h2>Редактировать картину: {{ painting.title }}</h2>
        {{ form.as_p }}
        <p><small>Укажите цену в выбранной валюте (будет конвертировано в евро)</small></p>
        <button type="submit">Сохранить</button>
    </form>
{% endblock %}
"""

# Сохранение шаблонов и создание директорий
os.makedirs(os.path.join(BASE_DIR, 'templates'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'media/paintings'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)

with open(os.path.join(BASE_DIR, 'templates/base.html'), 'w', encoding='utf-8') as f:
    f.write(base_html)
with open(os.path.join(BASE_DIR, 'templates/gallery_list.html'), 'w', encoding='utf-8') as f:
    f.write(gallery_list_html)
with open(os.path.join(BASE_DIR, 'templates/add_painting.html'), 'w', encoding='utf-8') as f:
    f.write(add_painting_html)
with open(os.path.join(BASE_DIR, 'templates/edit_painting.html'), 'w', encoding='utf-8') as f:
    f.write(edit_painting_html)

# Запуск проекта
if __name__ == "__main__":
    if len(sys.argv) > 1:
        call_command(sys.argv[1], *sys.argv[2:])
    else:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['main.py', 'runserver'])
