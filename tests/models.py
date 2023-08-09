from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.models import Orderable, Page, Site


class SimplePage(Page):
    body = models.TextField()

    def get_context(self, request):
        context = super(SimplePage, self).get_context(request)
        site = Site.find_for_request(request)
        context['breadcrumb'] = self.get_ancestors(inclusive=True).filter(depth__gte=site.root_page.depth)
        return context


class SimplePageRelatedLink(Orderable):
    page = ParentalKey(SimplePage, related_name='related_links')
    url = models.URLField()
    link_text = models.CharField(max_length=255)
