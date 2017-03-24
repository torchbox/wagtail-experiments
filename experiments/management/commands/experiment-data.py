from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db.models import F
from experiments.models import Experiment, ExperimentHistory
from random import randrange


class Command(BaseCommand):
    help = 'Creates history demo data for a ' \
           'Wagtail Experiment (A/B Testing).'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            'slug', help='Slug of the Wagtail Experiment '
                         'to supply with demo data or to purge '
                         'of its data.')

        # Named (optional) arguments
        parser.add_argument(
            '--days',
            type=int,
            default=10,
            help='Number of days to create demo '
                 'data for.',
        )
        parser.add_argument(
            '--min',
            type=int,
            default=100,
            help='Minimum number of session views for a '
                 'variation.',
        )
        parser.add_argument(
            '--max',
            type=int,
            default=150,
            help='Maximum number of session views for a '
                 'variation.',
        )
        parser.add_argument(
            '--purge',
            action='store_true',
            default=False,
            help='Purge specified Wagtail Experiment of '
                 'any existing history data.',
        )

    def write(self, text):
        self.stdout.write(text)

    def warn(self, text):
        decorated = self.style.WARNING(text)
        self.write(decorated)

    def oops(self, text):
        decorated = self.style.ERROR(text)
        self.write(decorated)

    def yeah(self, text):
        decorated = self.style.SUCCESS(text)
        self.write(decorated)

    def handle(self, *args, **options):
        slug = options.get('slug', '')
        purge = options.get('purge', False)
        days = options.get('days', 10)
        min_ = options.get('min', 100)
        max_ = options.get('max', 150)

        # Get the experiment by its slug
        try:
            experiment = Experiment.objects.get(slug=slug)
        except Experiment.DoesNotExist:
            return self.oops('No experiment with slug %s found. '
                             'Did you create it?' % slug)

        history = experiment.history.exists()

        # If --purge: purge and quit
        if purge:
            if not history:
                return self.write('Experiment %s has no history data to '
                                  'purge.' % experiment)
            ExperimentHistory.objects.filter(experiment=experiment).delete()
            return self.yeah('Deleted all history data for %s.' % experiment)

        # If not --purge: create demo data
        self.write('Creating demo history data for experiment '
                   '%s...' % experiment)
        self.write('Control pages will have a conversion rate of 1/4, '
                   'whereas other variations will have a rate of 1/3.')
        history and self.warn('Mind the already existing history data '
                              'for this experiment.')

        variations = experiment.get_variations()
        control = experiment.control_page

        for variation in variations:
            for day in range(0, days):
                date = datetime.now() - timedelta(days=day)
                hist_range = range(0, randrange(min_, max_ + 1))
                self.write('Adding %s views at %s for page %s...' %
                           (len(hist_range),
                            date.strftime('%b %d'),
                            variation))
                for x in hist_range:
                    history, _ = ExperimentHistory.objects.get_or_create(
                        experiment=experiment, variation=variation, date=date)

                    # Increment the participant_count
                    ExperimentHistory.objects.filter(pk=history.pk).update(
                        participant_count=F('participant_count') + 1)

                    if variation == control:
                        # Make the control page less likely to complete
                        if randrange(0, 4) == 1:
                            ExperimentHistory.objects.filter(pk=history.pk) \
                                .update(
                                    completion_count=F('completion_count') + 1)
                    else:
                        if randrange(0, 3) == 1:
                            ExperimentHistory.objects.filter(pk=history.pk) \
                                .update(
                                    completion_count=F('completion_count') + 1)

        self.yeah('All done creating data for experiment %s.' % experiment)
