from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()

LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
EDIT_URL = 'notes:edit'


class TestContent(TestCase):

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
            title='Заголовок',
            text='Текст',
            slug='pasport'
        )
        cls.url_list = LIST_URL
        cls.url_add = ADD_URL
        cls.url_edit = reverse(EDIT_URL, args=(cls.note.slug,))

    def test_note_in_list_for_author(self):
        """Отдельная заметка передаётся на страницу со списком заметок."""
        response = self.author_client.get(self.url_list)
        object = response.context['object_list']
        self.assertIn(self.note, object)

    def test_note_not_in_list_for_another_user(self):
        """В список заметок одного пользователя не попадают
        заметки другого пользователя.
        """
        response = self.reader_client.get(self.url_list)
        object = response.context['object_list']
        self.assertNotIn(self.note, object)

    def test_create_note_page_contains_form(self):
        """На страницу создания заметки передаются формы."""
        response = self.author_client.get(self.url_add)
        self.assertIn('form', response.context)
        form = response.context.get('form')
        self.assertIsInstance(form, NoteForm)

    def test_edit_note_page_contains_form(self):
        """На страницу редактирования заметки передаются формы."""
        response = self.author_client.get(self.url_edit)
        self.assertIn('form', response.context)
