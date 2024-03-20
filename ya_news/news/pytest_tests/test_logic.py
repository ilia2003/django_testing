from http import HTTPStatus

import pytest

from pytest_django.asserts import assertFormError, assertRedirects

from django.urls import reverse

from news.models import Comment

from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse('news:detail', args=(news.pk,))
    # Через анонимный клиент пытаемся создать заметку:
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    # Проверяем, что произошла переадресация на страницу логина:
    assertRedirects(response, expected_url)
    # Считаем количество заметок в БД, ожидаем 0 заметок.
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authorised_user_can_create_comment(author_client, form_data, news):
    url = reverse('news:detail', args=(news.pk,))
    # Через авторизованный клиент пытаемся создать заметку:
    response = author_client.post(url, data=form_data)
    expected_url = f'{url}#comments'
    # # Проверяем, что произошла переадресация на страницу поста
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1


@pytest.mark.django_db
# В параметрах вызвана фикстура comment: значит, в БД создан коммент.
def test_author_can_edit_comment(author_client, form_data, news, comment):
    # Получаем адрес страницы редактирования коммента:
    url = reverse('news:edit', args=(comment.pk,))
    succes_url = reverse('news:detail', args=(news.pk,))
    # В POST-запросе на адрес редактирования коммента
    # отправляем form_data - новые значения для полей коммента:
    response = author_client.post(url, form_data)
    expected_url = f'{succes_url}#comments'
    # Проверяем редирект:
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, news, comment):
    # Получаем адрес страницы удаления коммента:
    url = reverse('news:delete', args=(comment.pk,))
    succes_url = reverse('news:detail', args=(news.pk,))
    # В POST-запросе на адрес удаляем коммент с comment.pk
    response = author_client.post(url)
    expected_url = f'{succes_url}#comments'
    # Проверяем редирект:
    assertRedirects(response, expected_url)
    # Проверяем, что база пуста:
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    # Формируем словарь с запрещёнкой:
    bad_words_data = {'text': f'Smth text and {BAD_WORDS[0]}'}
    url = reverse('news:detail', args=(news.pk,))
    # Пытаемся создать коммент со стоп-словами:
    response = author_client.post(url, data=bad_words_data)
    # Проверяем, что форма выдала ошибку:
    assertFormError(response,
                    form='form',
                    field='text',
                    errors=WARNING)
    # Проверяем, что база пуста:
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(reader_client,
                                                news, comment, form_data):
    url = reverse('news:edit', args=(comment.pk,))
    comment_text = comment.text
    response = reader_client.post(url, data=form_data)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст остался тем же, что и был.
    assert comment.text == comment_text


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client,
                                                  news, comment, form_data):
    url = reverse('news:delete', args=(comment.pk,))
    # Выполняем запрос на удаление от пользователя-читателя.
    response = reader_client.delete(url)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Убедимся, что комментарий по-прежнему на месте.
    assert Comment.objects.count() == 1
