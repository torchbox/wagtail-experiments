from __future__ import absolute_import, unicode_literals

from hashlib import sha1
from importlib import import_module

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, InlinePanel
from wagtail.wagtailcore.models import Orderable


BACKEND = None


def get_backend():
    global BACKEND
    if BACKEND is None:
        backend_name = getattr(settings, 'WAGTAIL_EXPERIMENTS_BACKEND', 'experiments.backends.db')
        BACKEND = import_module(backend_name)

    return BACKEND


@python_2_unicode_compatible
class Experiment(ClusterableModel):
    STATUS_CHOICES = [
        ('draft', "Draft"),
        ('live', "Live"),
        ('completed', "Completed"),
    ]
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    control_page = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.CASCADE)
    goal = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    winning_variation = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.SET_NULL, null=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        PageChooserPanel('control_page'),
        InlinePanel('alternatives', label="Alternatives"),
        PageChooserPanel('goal'),
        FieldPanel('status'),
    ]

    def __init__(self, *args, **kwargs):
        super(Experiment, self).__init__(*args, **kwargs)
        self._initial_status = self.status

    def activate_alternative_draft_content(self):
        # For any alternative pages that are unpublished, copy the latest draft revision
        # to the main table (with is_live=False) so that the revision shown as an alternative
        # is not an out-of-date one
        for alternative in self.alternatives.select_related('page'):
            if not alternative.page.live:
                revision = alternative.page.get_latest_revision_as_page()
                revision.live = False
                revision.has_unpublished_changes = True
                revision.save()

    def get_variations(self):
        return [self.control_page] + [alt.page for alt in self.alternatives.select_related('page')]

    def get_variation_for_user(self, user_id):
        variations = self.get_variations()

        # choose uniformly from variations, based on a hash of user_id and experiment.slug
        hash_input = "{0}.{1}".format(self.slug, user_id)
        hash_str = sha1(hash_input.encode('utf-8')).hexdigest()[:7]
        variation_index = int(hash_str, 16) % len(variations)
        return variations[variation_index]

    def start_experiment_for_user(self, user_id, request):
        """
        Record a new participant and return the variation for them to use
        """
        variation = self.get_variation_for_user(user_id)
        get_backend().record_participant(self, user_id, variation, request)
        return variation

    def record_completion_for_user(self, user_id, request):
        backend = get_backend()
        variation = self.get_variation_for_user(user_id)
        backend.record_completion(self, user_id, variation, request)

    def select_winner(self, variation):
        self.winning_variation = variation
        self.status = 'completed'
        self.save()

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
