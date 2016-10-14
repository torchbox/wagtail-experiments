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


class ExperimentModelAdmin(ModelAdmin):
    model = Experiment
    add_to_settings_menu = True

modeladmin_register(ExperimentModelAdmin)


@hooks.register('before_serve_page')
def check_experiments(page, request, serve_args, serve_kwargs):
    # If the page being served is the control page of an experiment, run the experiment
    experiments = Experiment.objects.filter(control_page=page)
    if experiments:
        experiment = experiments[0]
        user_id = request.session.setdefault('experiment_user_id', str(uuid.uuid4()))
        variation = experiment.get_variation_for_user(user_id)

        get_backend().record_participant(experiment, user_id, variation)

        if variation.pk != page.pk:
            # serve this alternative instead of the current page
            return variation.specific.serve(request, *serve_args, **serve_kwargs)
