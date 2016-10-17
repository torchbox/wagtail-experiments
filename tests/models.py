from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page


class SimplePage(Page):
    body = models.TextField()
