import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_of_news_sorting(bulk_news, client, news_home_url):
    response = client.get(news_home_url)
    assert 'object_list' in response.context
    all_dates = [news.date for news in response.context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


def test_news_count(bulk_news, client, news_home_url):
    response = client.get(news_home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_comments_sorting(client, news_detail_url):
    all_dates = [comment.created for comment in
                 client.get(news_detail_url).context['news'].comment_set.all()]
    assert all_dates == sorted(all_dates)


def test_form_for_logedin_user(reader_client, news_detail_url):
    assert isinstance(
        reader_client.get(news_detail_url).context.get('form'),
        CommentForm
    )


def test_form_for_anonymous_user(client, news_detail_url):
    assert 'form' not in client.get(news_detail_url).context
