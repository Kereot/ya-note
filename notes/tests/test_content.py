from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotes(TestCase):
    TEST_LIMIT = 10

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='user')

        # Не получается применить bulk_create(), чтобы генерировался slug.
        for i in range(cls.TEST_LIMIT):
            note = Note.objects.create(
                title=f'note {i}',
                text='content',
                author=cls.author,
            )
            note.save()

        cls.note = Note.objects.create(
            title=f'note {cls.TEST_LIMIT}',
            text='content',
            author=cls.author,
            slug='note-slug',
        )
        cls.note.save()

    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        all_ids = [note.id for note in object_list]
        sorted_ids = sorted(all_ids)
        self.assertEqual(all_ids, sorted_ids)

    def test_slug_formatting(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        for obj in object_list[:self.TEST_LIMIT]:
            self.assertEqual(obj.slug, slugify(obj.title))
        special_obj = object_list[self.TEST_LIMIT]
        self.assertNotEqual(special_obj.slug, slugify(special_obj.title))

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        note_slug = self.note.slug
        url_names = (
            ('notes:add', None),
            ('notes:edit', (note_slug,)),
        )
        for name, args in url_names:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
