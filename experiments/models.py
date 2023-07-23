from hashlib import sha1
from importlib import import_module
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

try:
    from wagtail.models import Page
    from wagtail.admin.panels import FieldPanel, PageChooserPanel, InlinePanel
except ImportError:  # fallback for Wagtail <5.0
    from wagtail.core.models import Page
    from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel, InlinePanel
from wagtail.models import Orderable

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

BACKEND = None


def get_backend():
    '''
        Get the backend to use for wagtail-experiments.

        Args:
            None

        Return:
            Backend module.
            If WAGTAIL_EXPERIMENTS_BACKEND not defined, defaults to experiments.backends.db.
    '''

    global BACKEND
    if BACKEND is None:
        backend_name = getattr(settings, 'WAGTAIL_EXPERIMENTS_BACKEND', 'experiments.backends.db')
        BACKEND = import_module(backend_name)

    return BACKEND


class Experiment(ClusterableModel):
    '''
        Define an experiment for a page.
    '''

    STATUS_CHOICES = [
        ('draft', _("Draft")),
        ('live', _("Live")),
        ('completed', _("Completed")),
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
        InlinePanel('alternatives', heading=_("Alternatives"), label=_("Alternative")),
        PageChooserPanel('goal'),
        FieldPanel('status'),
    ]


    class Meta:
        verbose_name = _('Experiment')
        verbose_name_plural = _('Experiments')


    def __init__(self, *args, **kwargs):
        '''
            Initiate an experiment for a page. Set the
            _initial_status to the experiment's status.

            Args:
                self:    instance of the class Experiment
                args:    positional arguments to initiate experiment
                kwargs:  keyword arguments to initiate experiment

            Return:
                Nothing
        '''

        super(Experiment, self).__init__(*args, **kwargs)
        self._initial_status = self.status

    def activate_alternative_draft_content(self):
        '''
            For any alternative pages that are unpublished, copy the latest
            draft revision to the main table (with is_live=False) so that the
            revision shown as an alternative is not an out-of-date one.

            Args:
                self: instance of the class Experiment

            Return:
                Nothing
        '''

        for alternative in self.alternatives.select_related('page'):
            if not alternative.page.live:
                try:
                    revision = alternative.page.get_latest_revision_as_object()
                except AttributeError:  # fallback for Wagtail <2.3
                    revision = alternative.page.get_latest_revision_as_page()
                revision.live = False
                revision.has_unpublished_changes = True
                revision.save()

    def get_variations(self):
        '''
            Get all the variations for the control page.

            If the alternative has "use_control_title" set, then
            change the alternative's title to match the control's title.

            Args:
                self: instance of the class Experiment

            Return:
                variations: a list with the control page and all alternatives
        '''

        variations = [self.control_page]
        for alternative in self.alternatives.select_related('page'):
            if alternative.use_control_title:
                alternative.page.title = self.control_page.title
            variations.append(alternative.page)

        return variations

    def get_variation_for_user(self, user_id):
        '''
            Get a page variation for this user and request session.

            Args:
                self:    instance of the class Experiment
                user_id: the id for this user

            Return:
                variation: a page variation
        '''

        variations = self.get_variations()

        hash_input = "{0}.{1}".format(self.slug, user_id)
        # does this distribute variations evenly?
        # we probably need to track number of times each
        # variation is selected, sort by count, and choose the lowest
        hash_str = sha1(hash_input.encode('utf-8')).hexdigest()[:7]
        variation_index = int(hash_str, 16) % len(variations)

        return variations[variation_index]

    def start_experiment_for_user(self, user_id, request):
        '''
            Record a new participant and return the variation for them to use.

            Args:
                self:    instance of the class Experiment
                user_id: the id for this user
                request: django HttpRequest

            Return:
                Variation the user will see
        '''

        variation = self.get_variation_for_user(user_id)
        get_backend().record_participant(self, user_id, variation, request)
        return variation

    def record_completion_for_user(self, user_id, request):
        '''
            Record the completion of the variation for the user.

            Args:
                self:    instance of the class Experiment
                user_id: the id for this user
                request: django HttpRequest

            Return:
                Nothing

            Is the following appropriate? Or should we only consider it a win if
            the user sees an experiment page and immediately goes to the goal?
                If:
                    1. The user goes to a experiment page
                    2. Then wanders the site for hours
                    3. Finally hits a goal page
                Then:
                    We record a win for the experiment. It isn't.
        '''

        backend = get_backend()
        variation = self.get_variation_for_user(user_id)
        backend.record_completion(self, user_id, variation, request)

    def select_winner(self, variation):
        '''
            Save the variation that won.

            Args:
                self:      instance of the class Experiment
                variation: winning variation

            Return:
                Nothing
        '''

        self.winning_variation = variation
        self.status = 'completed'
        self.save()

    def __str__(self):
        '''
            Args:
                self: instance of the class Experiment

            Return:
                the experiment's name
        '''

        return self.name


class Alternative(Orderable):
    '''
        Alternative page for the control page.
    '''

    experiment = ParentalKey(Experiment, related_name='alternatives', on_delete=models.CASCADE)
    page = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.CASCADE)
    use_control_title = models.BooleanField(_("Use Control's Title"), default=False)

    panels = [
        PageChooserPanel('page'),
        FieldPanel("use_control_title"),
    ]

    class Meta:
        verbose_name = _('Alternative')
        verbose_name_plural = _('Alternatives')


class ExperimentHistory(models.Model):
    '''
        Maintains the number of participants and completions
        on a given day for a given variation of an experiment.
    '''

    experiment = models.ForeignKey(Experiment, related_name='history', on_delete=models.CASCADE)
    date = models.DateField()
    variation = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.CASCADE)
    participant_count = models.PositiveIntegerField(default=0)
    completion_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [
            ('experiment', 'date', 'variation'),
        ]

        verbose_name = _('Experiment History')
        verbose_name_plural = _('Experiment Histories')
