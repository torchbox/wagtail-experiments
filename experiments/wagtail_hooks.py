from __future__ import absolute_import, unicode_literals

from importlib import import_module
import uuid

from django.conf import settings

from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.wagtailcore import hooks

from .models import Experiment


BACKEND = None


def get_backend():
    global BACKEND
    if BACKEND is None:
        backend_name = getattr(settings, 'WAGTAIL_EXPERIMENTS_BACKEND', 'experiments.backends.db')
        BACKEND = import_module(backend_name)

    return BACKEND


def get_user_id(request):
    return request.session.setdefault('experiment_user_id', str(uuid.uuid4()))


class ExperimentModelAdmin(ModelAdmin):
    model = Experiment
    add_to_settings_menu = True

modeladmin_register(ExperimentModelAdmin)


@hooks.register('before_serve_page')
def check_experiments(page, request, serve_args, serve_kwargs):
    # TODO: Do not count goal twice (probably should be in backend)

    # If the page being served is the goal page of an experiment, log a completion
    completed_experiments = Experiment.objects.filter(goal=page, status='live')

    if completed_experiments:
        backend = get_backend()
        user_id = get_user_id(request)

        for experiment in completed_experiments:
            variation = experiment.get_variation_for_user(user_id)
            backend.record_completion(experiment, user_id, variation)

    # If the page being served is the control page of an experiment, run the experiment
    experiments = Experiment.objects.filter(control_page=page, status__in=('live', 'completed'))
    if experiments:
        experiment = experiments[0]

        if experiment.status == 'completed' and experiment.winning_variation is not None:
            variation = experiment.winning_variation
        else:
            user_id = get_user_id(request)
            variation = experiment.get_variation_for_user(user_id)

            get_backend().record_participant(experiment, user_id, variation)

        if variation.pk != page.pk:
            # serve this alternative instead of the current page

            variation = variation.specific

            # hack the title and page-tree-related fields to match the control page
            variation.id = page.id
            variation.pk = page.pk
            variation.path = page.path
            variation.depth = page.depth
            variation.url_path = page.url_path
            variation.title = page.title

            return variation.serve(request, *serve_args, **serve_kwargs)
