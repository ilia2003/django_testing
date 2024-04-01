from http import HTTPStatus

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING
from .configurations import TestBaseParameters, Urls


class TestClass(TestBaseParameters):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_created_note_with_and_without_slug(self):
        creation_cases = (
            (self.new_note_data, self.new_note_data['slug']),
            (self.no_slug_note_data, slugify(self.no_slug_note_data['title'])),
        )
        for data, expected_slug in creation_cases:
            with self.subTest(data=data, expected_slug=expected_slug):
                notes_at_start = set(Note.objects.all())
                self.assertRedirects(
                    self.author_client.post(Urls.NOTE_ADD, data=self.data),
                    Urls.NOTES_SUCCESS
                )
                note_objects = (set(Note.objects.all()) - notes_at_start)
                self.assertEqual(len(note_objects), 1)
                note = note_objects.pop()
                self.assertEqual(note.slug, self.data['slug'])
                self.assertEqual(note.title, self.data['title'])
                self.assertEqual(note.text, self.data['text'])
                self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_before = Note.objects.count()
        self.assertRedirects(
            self.client.post(Urls.NOTE_ADD, data=self.new_note_data),
            Urls.REDIRECT_TO_NOTE_ADD
        )
        self.assertEqual(
            notes_before, Note.objects.count()
        )

    def test_cant_use_slug_again(self):
        notes_before = Note.objects.count()
        self.new_note_data['slug'] = self.note.slug
        self.assertFormError(
            self.author_client.post(Urls.NOTE_ADD, data=self.new_note_data),
            form='form',
            field='slug',
            errors=self.new_note_data['slug'] + WARNING
        )
        self.assertEqual(
            notes_before, Note.objects.count()
        )

    def test_author_can_edit(self):
        self.assertEqual(
            self.reader_client.post(
                Urls.NOTE_EDIT, data=self.edit_note_data
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.note.slug)

    def test_author_can_delete_note(self):
        notes_before = Note.objects.count()
        self.author_client.delete(Urls.NOTE_DELETE)
        self.assertEqual(notes_before, Note.objects.count() + 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_reader_cant_delete_note(self):
        self.reader_client.delete(Urls.NOTE_DELETE)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)
        self.assertEqual(note.slug, self.note.slug)
