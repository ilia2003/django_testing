from notes.forms import NoteForm
from .configurations import TestBaseParameters, Urls


class TestContent(TestBaseParameters):

    def test_note_displays_for_author(self):
        response = self.author_client.get(Urls.NOTES_LIST)
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertIn(
            self.note,
            object_list,
        )

    def test_note_displays_for_reader(self):
        self.assertNotIn(
            self.note,
            self.reader_client.get(Urls.NOTES_LIST).context['object_list']
        )

    def test_form_at_add_and_edit_urls(self):
        testing_urls = (
            Urls.NOTE_EDIT, Urls.NOTE_ADD
        )
        for url in testing_urls:
            with self.subTest(url=url):
                self.assertIsInstance(
                    self.author_client.get(url).context.get('form'),
                    NoteForm
                )
