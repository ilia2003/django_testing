import pytest

from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.test.client import Client

from news.models import News, Comment
# Импортируем модель новости и коммента, чтобы создать экземпляры.
# Текущая дата.
today = datetime.today()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Author')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Reader')


@pytest.fixture
def reader_client(reader, Client):  # Вызываем фикстуру автора и клиента.
    Client.force_login(reader)  # Логиним автора в клиенте.
    return Client


@pytest.fixture
def author_client(author, Client):  # Вызываем фикстуру автора и клиента.
    Client.force_login(author)  # Логиним автора в клиенте.
    return Client


@pytest.fixture
def news():
    news = News.objects.create(  # Создаём объект новости.
        title='Title',
        text='Some text',
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(  # Создаём объект коммента.
        news=news,
        text='My useful comment',
        author=author,
    )
    return comment


@pytest.fixture
def news_list():
    today = datetime.today()
    all_news = []
    for index in range(NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Title {index}',
            text='Just a text.',
            date=today - timedelta(days=index)
        )
        all_news.append(news)
    News.objects.bulk_create(all_news)


@pytest.fixture
def comments_list(news, author):
    now = timezone.now()
    for index in range(2):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Text {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()
# @pytest.fixture
# def form_data():
#     return {
#         'text': 'New text',
#     }
