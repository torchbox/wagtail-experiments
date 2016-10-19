from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page


class SimplePage(Page):
    body = models.TextField()

    def get_context(self, request):
        context = super(SimplePage, self).get_context(request)
        context['breadcrumb'] = self.get_ancestors(inclusive=True).filter(depth__gte=request.site.root_page.depth)
        return context
