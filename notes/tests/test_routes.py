from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.other_user = User.objects.create(username='other_user')
        cls.note = Note.objects.create(
            title='note',
            text='content',
            slug='slug',
            author=cls.author
        )

    def test_home_page(self):
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_access(self):
        self.client.force_login(self.other_user)
        url_names = (
            'notes:add',
            'notes:list',
            'notes:success',
        )
        for name in url_names:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_access(self):
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.other_user, HTTPStatus.NOT_FOUND),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            note_slug = self.note.slug
            url_names = (
                'notes:edit',
                'notes:detail',
                'notes:delete',
            )
            for name in url_names:
                with self.subTest(name=name):
                    url = reverse(name, args=(note_slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_anonymous_redirect(self):
        login_url = reverse('users:login')
        note_slug = self.note.slug
        url_names = (
            ('notes:add', None),
            ('notes:edit', (note_slug,)),
            ('notes:detail', (note_slug,)),
            ('notes:delete', (note_slug,)),
            ('notes:list', None),
            ('notes:success', None),
        )
        for name, args in url_names:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
