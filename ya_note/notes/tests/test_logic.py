from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
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


class TestNoteCreation(TestCase):

    NEW_NOTE_TITLE = 'Новый текст заголовка заметки'
    NEW_NOTE_TEXT = 'Новый текст заметки'
    NEW_NOTE_SLUG = 'kniga'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.url = reverse(ADD_URL)
        cls.url_sussess = (SUCCESS_URL)
        cls.form_data = {'title': cls.NEW_NOTE_TITLE,
                         'text': cls.NEW_NOTE_TEXT,
                         'slug': cls.NEW_NOTE_SLUG,
                         }

    def test_user_cant_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        self.author_client.post(self.url, data=self.form_data)
        notes_cout = Note.objects.count()
        self.assertEqual(notes_cout, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)


class TestNoteEditDelete(TestCase):

    NOTE_TITLE = "Заголовок заметки"
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'pasport'

    NEW_NOTE_TITLE = 'Новый текст заголовка заметки'
    NEW_NOTE_TEXT = 'Новый текст заметки'
    NEW_NOTE_SLUG = 'kniga'

    @classmethod
    def setUpTestData(cls):

        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            author=cls.author,
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG
        )
        cls.url_add = reverse(ADD_URL)
        cls.url_success = reverse(SUCCESS_URL)
        cls.url = reverse(DETAIL_URL, args=(cls.note.slug,))
        cls.url_edit = reverse(EDIT_URL, args=(cls.note.slug,))
        cls.url_delete = reverse(DELETE_URL, args=(cls.note.slug,))

        cls.form_data = {'title': cls.NEW_NOTE_TEXT,
                         'text': cls.NEW_NOTE_TEXT,
                         'slug': cls.NEW_NOTE_SLUG}

    def test_author_can_delete_note(self):
        """Автор может удалять свои заметки."""
        notes_count_before = Note.objects.count()
        self.assertEqual(notes_count_before, 1)
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response, self.url_success)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Читатель не может удалять чужие заметки."""
        response = self.reader_client.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        response = self.author_client.post(self.url_edit, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_notes_of_another_user(self):
        """Читатель не может редактировать чужие заметки."""
        response = self.reader_client.post(self.url_edit, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)


class TestNoteCreationSlug(TestCase):

    NOTE_TITLE = "Заголовок заметки"
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'pasport'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            author=cls.author,
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG
        )

        cls.url = reverse(ADD_URL)

    def test_user_cant_use_warning(self):
        """Нельзя создать заметку с существующим slug."""
        warning_data_slug = {
            'title': 'Заголовок из формы',
            'text': 'Текст из формы',
            'slug': 'pasport',
        }
        note_before = Note.objects.count()
        self.assertEqual(note_before, 1)
        response = self.author_client.post(self.url, data=warning_data_slug)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors='pasport' + WARNING
        )

        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, 1)


class TestEmptySlug(TestCase):

    NEW_NOTE_TITLE = 'Новый текст заголовка заметки'
    NEW_NOTE_TEXT = 'Новый текст заметки'
    NEW_NOTE_SLUG = 'kniga'

    @classmethod
    def setUpTestData(cls):

        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.url_add = reverse(ADD_URL)
        cls.form_data = {'title': cls.NEW_NOTE_TEXT,
                         'text': cls.NEW_NOTE_TEXT,
                         'slug': cls.NEW_NOTE_SLUG}

    def test_empty_slug(self):
        """Если при создании заметки не заполнен slug,
        то он формируется автоматически.
        """
        self.form_data.pop('slug',)
        self.author_client.post(self.url_add, data=self.form_data)
        assert Note.objects.count() == 1
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        assert new_note, expected_slug
