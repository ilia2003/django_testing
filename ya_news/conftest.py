from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.utils import timezone
from django.urls import reverse


from news.models import News, Comment
from news.forms import BAD_WORDS

NEWS_DETAIL_URL = 'news:detail'
NEWS_DELETE_URL = 'news:delete'
NEWS_EDIT_URL = 'news:edit'
client = Client()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def anonymous_client(client):
    return client


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(news=news,
                                  author=author,
                                  text='Текст комментария')


# @pytest.fixture
# def slug_for_args(news):
#     return (news.id,)


@pytest.fixture
def all_news(news):
    today = datetime.today()
    all_new = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_new)


@pytest.fixture
def comments(news, author):
    author = author
    now = timezone.now()
    comments = []
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return comments


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст'
    }


@pytest.fixture
def bad_words_data():
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


@pytest.fixture
def slug_for_comment(news, comment):
    return (comment.id,)


@pytest.fixture
def news_delete_url(slug_for_args):
    return reverse(NEWS_DELETE_URL, args=slug_for_args)


@pytest.fixture
def news_detail_url(slug_for_args):
    return reverse(NEWS_DETAIL_URL, args=slug_for_args)


@pytest.fixture
def news_edit_url(slug_for_args):
    return reverse(NEWS_EDIT_URL, args=slug_for_args)
