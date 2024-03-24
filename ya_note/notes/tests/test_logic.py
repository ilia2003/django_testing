from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            slug='slug',
            author=cls.author,)
        cls.url = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data_note = {'title': 'Another title',
                              'text': 'Another text',
                              'slug': 'another_slug',
                              'author': cls.author}

    def test_add_note_anonim(self):
        self.client.post(self.url, data=self.form_data_note)
        count_notes = Note.objects.count()
        self.assertEqual(count_notes, 0)

    def test_add_note_author(self):
        response = self.author_client.post(self.url, data=self.form_data_note)
        count_notes = Note.objects.count()
        self.assertRedirects(response, self.url_success)
        self.assertEqual(count_notes, 2)
        new_note = Note.objects.get(id.alast())
        self.assertEqual(new_note.title, self.form_data_note['title'])
        self.assertEqual(new_note.text, self.form_data_note['text'])
        self.assertEqual(new_note.slug, self.form_data_note['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_not_unique_slug(self):
        self.form_data_note['slug'] = self.note.slug
        response = self.author_client.post(self.url, data=self.form_data_note)
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        assert Note.objects.count() == 1

    def test_empty_slug(self):
        self.form_data_note.pop('slug')
        response = self.author_client.post(self.url, data=self.form_data_note)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.get(id=2)
        expected_slug = slugify(self.form_data_note['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url,
                                           data=self.form_data_note)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data_note['title'])
        self.assertEqual(self.note.text, self.form_data_note['text'])
        self.assertEqual(self.note.slug, self.form_data_note['slug'])

    def test_reader_can_not_edit_note(self):
        response = self.reader_client.post(self.edit_url,
                                           data=self.form_data_note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.url_success)
        assert Note.objects.count() == 0

    def test_reader_can_not_delete_note(self):
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        assert Note.objects.count() == 1
