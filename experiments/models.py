from __future__ import absolute_import, unicode_literals

from hashlib import sha1

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, InlinePanel
from wagtail.wagtailcore.models import Orderable


@python_2_unicode_compatible
class Experiment(ClusterableModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    control_page = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.CASCADE)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        PageChooserPanel('control_page'),
        InlinePanel('alternatives', label="Alternatives"),
    ]

    def get_variations(self):
        return [self.control_page] + [alt.page for alt in self.alternatives.select_related('page')]

    def get_variation_for_user(self, user_id):
        variations = self.get_variations()

        # choose uniformly from variations, based on a hash of user_id and experiment.slug
        hash_input = "{0}.{1}".format(self.slug, user_id)
        hash_str = sha1(hash_input.encode('utf-8')).hexdigest()[:7]
        variation_index = int(hash_str, 16) % len(variations)
        return variations[variation_index]

    def __str__(self):
        return self.name


class Alternative(Orderable):
    experiment = ParentalKey(Experiment, related_name='alternatives', on_delete=models.CASCADE)
    page = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('page'),
    ]


class ExperimentHistory(models.Model):
    """
    Records the number of participants and completions on a given day for a given variation of an experiment
    """
    experiment = models.ForeignKey(Experiment, related_name='history', on_delete=models.CASCADE)
    date = models.DateField()
    variation = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.CASCADE)
    participant_count = models.PositiveIntegerField(default=0)
    completion_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [
            ('experiment', 'date', 'variation'),
        ]
