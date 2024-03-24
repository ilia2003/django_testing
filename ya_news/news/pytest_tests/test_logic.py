from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import WARNING

LOGIN_URL = reverse('users:login')


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data,
                                            news_detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    comment_count = Comment.objects.count()
    assert comment_count == 0
    response = client.post(news_detail_url, data=form_data)
    expected_url = f'{LOGIN_URL}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_cant_create_comment(author_client, news_detail_url, form_data):
    """Авторизованный пользователь может отправить комментарий."""
    response = author_client.post(news_detail_url, data=form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']


def test_user_cant_use_bad_words(author_client,
                                 bad_words_data,
                                 news_detail_url):
    """Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    comment_bad_words = Comment.objects.count()
    assert comment_bad_words == 0
    response = author_client.post(news_detail_url,
                                  data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client,
                                 comment, form_data,
                                 news_edit_url,
                                 news_detail_url):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = author_client.post(news_edit_url, form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == comment.author
    assert comment.news == comment.news


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(admin_client,
                                                news_edit_url,
                                                form_data,
                                                comment):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = admin_client.post(news_edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment.author
    assert comment.news == comment.news


def test_author_can_detele_comment(author_client,
                                   comment,
                                   news_delete_url,
                                   news_detail_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_count = Comment.objects.count()
    assert comments_count == 1
    response = author_client.post(news_delete_url)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(admin_client,
                                                  news_delete_url,
                                                  form_data,
                                                  comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    response = admin_client.post(news_delete_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
