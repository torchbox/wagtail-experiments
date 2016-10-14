from __future__ import absolute_import, unicode_literals

from django.test import TestCase


class TestIndexView(TestCase):
    def test_simple(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
