from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

HOME_URL = reverse('news:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
ADMIN_CLIENT = pytest.lazy_fixture('admin_client')
CLIENT = pytest.lazy_fixture('anonymous_client')
DELETE_URL = pytest.lazy_fixture('news_delete_url')
DETAIL_URL = pytest.lazy_fixture('news_detail_url')
EDIT_URL = pytest.lazy_fixture('news_edit_url')
OK_200 = HTTPStatus.OK
NOT_FOUND_404 = HTTPStatus.NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, status, user',
    (
        (DETAIL_URL, OK_200, CLIENT),
        (HOME_URL, OK_200, CLIENT),
        (LOGIN_URL, OK_200, CLIENT),
        (LOGOUT_URL, OK_200, CLIENT),
        (SIGNUP_URL, OK_200, CLIENT),
        (EDIT_URL, NOT_FOUND_404, CLIENT),
        (DELETE_URL, NOT_FOUND_404, CLIENT),
    ),
)
def test_availability_and_redirects_for_anonymous_user(url, status, user):
    response = user.get(url)
    if status == OK_200:
        assert response.status_code == status
    elif status == NOT_FOUND_404:
        expected_url = f'{LOGIN_URL}?next={url}'
        assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (ADMIN_CLIENT, NOT_FOUND_404),
        (AUTHOR_CLIENT, OK_200)
    ),
)
@pytest.mark.parametrize(
    'url',
    (EDIT_URL, DELETE_URL),
)
def test_pages_availability_for_author(
    parametrized_client,
    url,
    comment,
    expected_status
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status
