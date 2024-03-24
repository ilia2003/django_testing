from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from django.urls import reverse
from notes.models import Note

User = get_user_model()

HOME_URL = reverse('notes:home')
LIST_URL = 'notes:list'
ADD_URL = 'notes:add'
DELETE_URL = 'notes:delete'
EDIT_URL = 'notes:edit'
DETAIL_URL = 'notes:detail'
SUCCESS_URL = 'notes:success'
LOGIN_URL = 'users:login'
LOGOUT_URL = 'users:logout'
SIGNUP_URL = 'users:signup'


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст',
            slug='pasport'
        )

    def test_home_page(self):
        """Главная страница доступна анонимному пользователю."""
        response = self.client.get(HOME_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail(self):
        """Страницы отдельной заметки, доступны только автору заметки."""
        url = reverse(DETAIL_URL, args=(self.note.slug,))
        response = self.author_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability(self):
        """Страницы регистрации пользователей, входа в учётную запись
        и выхода из неё доступны всем пользователям.
        """
        urls = (
            (LOGIN_URL, None),
            (LOGOUT_URL, None),
            (SIGNUP_URL, None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client_list_success_add(self):
        """Редирекст на страницу логина."""
        login_url = reverse(LOGIN_URL)
        urls = (
            (LIST_URL, None),
            (SUCCESS_URL, None),
            (ADD_URL, None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_redirect_for_anonymous_client_edit_delete(self):
        """Удаление и редактирование заметки доступно только автору."""
        login_url = reverse(LOGIN_URL)
        for name in (DELETE_URL, EDIT_URL):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_author_notes_done_add(self):
        urls = (
            (LIST_URL, None),
            (SUCCESS_URL, None),
            (ADD_URL, None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
