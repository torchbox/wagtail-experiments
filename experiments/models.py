from __future__ import absolute_import, unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, InlinePanel
from wagtail.wagtailcore.models import Orderable


@python_2_unicode_compatible
class Experiment(ClusterableModel):
    name = models.CharField(max_length=255)
    control_page = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.CASCADE)

    panels = [
        FieldPanel('name'),
        PageChooserPanel('control_page'),
        InlinePanel('alternatives', label="Alternatives"),
    ]

    def __str__(self):
        return self.name


class Alternative(Orderable):
    experiment = ParentalKey(Experiment, related_name='alternatives', on_delete=models.CASCADE)
    page = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('page'),
    ]
