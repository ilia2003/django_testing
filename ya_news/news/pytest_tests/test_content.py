import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.fixture
def fixtere_reverse():
    HOME_URL = reverse('news:home')
    return HOME_URL


@pytestmark
def test_news_count(client, all_news, fixtere_reverse):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(fixtere_reverse)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytestmark
def test_news_order(fixtere_reverse, client, all_news):
    """Новости отсортированы от самой свежей к самой старой."""
    response = client.get(fixtere_reverse)
    object = response.context['object_list']
    all_dates = [news.date for news in object]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytestmark
def test_comments_order(client, news, slug_for_comment):
    """Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка,
    новые — в конце.
    """
    detail_url = reverse('news:detail', args=slug_for_comment)
    response = client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments.created


@pytestmark
def test_authorized_client_has_form(author_client,
                                    news_detail_url):
    """Авторизированному пользователю доступна форма для отправки
    комментария на странице отдельной новости.
    """
    response = author_client.get(news_detail_url)
    assert 'form' in response.context
    form = response.context.get('form')
    assert isinstance(form, CommentForm)


@pytestmark
def test_anonymous_client_has_no_form(client,
                                      news_detail_url):
    """Неавторизованному пользователю недоступна форма для отправки
    комментария на странице отдельной новости
    """
    response = client.get(news_detail_url)
    assert 'form' not in response.context
