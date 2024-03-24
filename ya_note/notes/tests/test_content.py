from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()
LIST_URL = reverse('notes:list')


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.reader = User.objects.create(username='Reader')
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            slug='first_slug',
            author=cls.author,)

    def test_note_in_object_list_author(self):
        self.client.force_login(self.author)
        response = self.client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_in_object_list_another_user(self):
        self.client.force_login(self.reader)
        response = self.client.get(LIST_URL)
        object = response.context['object_list']
        self.assertNotIn(self.note, object)

    def test_author_has_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            self.client.force_login(self.author)
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
