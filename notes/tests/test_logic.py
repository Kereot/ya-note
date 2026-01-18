from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': 'title',
            'text': 'content',
            'slug': 'slug',
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(reverse('notes:add'), self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_authorized_user_can_create_note(self):
        self.auth_client.post(reverse('notes:add'), self.form_data)
        self.assertEqual(Note.objects.count(), 1)


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.other_user = User.objects.create(username='other_user')
        cls.other_user_client = Client()
        cls.other_user_client.force_login(cls.other_user)
        cls.note = Note.objects.create(
            title='title',
            text='content',
            author=cls.author,
            slug='slug',
        )
        cls.note.save()
        cls.delete_note_url = reverse(
            'notes:delete',
            args=(cls.note.slug,)
        )
        cls.update_note_url = reverse(
            'notes:edit',
            args=(cls.note.slug,)
        )
        cls.form_data = {
            'title': 'title',
            'text': 'updated_content',
            'slug': 'slug',
        }

    def test_other_user_cant_delete_note(self):
        response = self.other_user_client.delete(self.delete_note_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_note_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_edit_note(self):
        note_text = self.note.text
        response = self.other_user_client.post(
            self.update_note_url,
            self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, note_text)

    def test_author_can_edit_note(self):
        note_text = self.form_data['text']
        response = self.author_client.post(
            self.update_note_url,
            self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, note_text)
