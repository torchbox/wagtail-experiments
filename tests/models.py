from __future__ import absolute_import, unicode_literals

from django.db import models

from modelcluster.fields import ParentalKey

try:
    from wagtail.core.models import Page, Orderable
except ImportError:  # fallback for Wagtail <2.0
    from wagtail.wagtailcore.models import Page, Orderable


class SimplePage(Page):
    body = models.TextField()

    def get_context(self, request):
        context = super(SimplePage, self).get_context(request)
        context['breadcrumb'] = self.get_ancestors(inclusive=True).filter(depth__gte=request.site.root_page.depth)
        return context


class SimplePageRelatedLink(Orderable):
    page = ParentalKey(SimplePage, related_name='related_links')
    url = models.URLField()
    link_text = models.CharField(max_length=255)
