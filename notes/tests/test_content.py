from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotes(TestCase):
    TEST_LIMIT = 10

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='user')
        cls.not_author = User.objects.create(username='not_author')

        # Не получается применить bulk_create(), чтобы генерировался slug.
        # Изначально я на них проверял создание slug, но в итоговом задании,
        # написано, что это нужно сделать в test_logic: переделал
        # соответствующий тест по аналогии с примером для pytest.
        for i in range(cls.TEST_LIMIT):
            note = Note.objects.create(
                title=f'note {i}',
                text='content',
                author=cls.author,
            )
            note.save()
        cls.note = Note.objects.create(
            title='title',
            text='content',
            author=cls.author,
        )
        cls.note.save()

    def test_not_author_has_no_note(self):
        self.client.force_login(self.not_author)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_author_has_notes_in_order(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        all_ids = [note.id for note in object_list]
        sorted_ids = sorted(all_ids)
        self.assertEqual(all_ids, sorted_ids)

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
