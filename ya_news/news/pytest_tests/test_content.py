import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_list_for_different_users(client, news_list):
    response = client.get(HOME_URL)
    object = response.context['object_list']
    news_count = len(object)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_list):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, slug_for_comment):
    detail_url = reverse('news:detail', args=slug_for_comment)
    response = client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created, all_comments[1].created


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, news_detail):
    response = author_client.get(news_detail)
    assert 'form' in response.context
    form = response.context.get('form')
    assert isinstance(form, CommentForm)


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_detail):
    response = client.get(news_detail)
    assert 'form' not in response.context
