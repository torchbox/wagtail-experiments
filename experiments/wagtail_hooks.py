from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url
from django.contrib.admin.utils import quote
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
import user_agents
from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.modeladmin.views import CreateView, EditView
from wagtail.wagtailcore import hooks

from experiments import admin_urls
from .models import Experiment
from .utils import get_user_id, impersonate_other_page


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^experiments/', include(admin_urls, app_name='experiments', namespace='experiments')),
    ]


class ExperimentButtonHelper(ButtonHelper):
    def report_button(self, pk, classnames_add=[], classnames_exclude=[]):
        classnames = classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            'url': reverse('experiments:report', args=(quote(pk), )),
            'label': _('Show report'),
            'classname': cn,
            'title': _('Report for this %s') % self.verbose_name,
        }

    def get_buttons_for_obj(self, obj, exclude=[], classnames_add=[],
                            classnames_exclude=[]):
        ph = self.permission_helper
        pk = quote(getattr(obj, self.opts.pk.attname))
        btns = super(ExperimentButtonHelper, self).get_buttons_for_obj(obj, exclude, classnames_add, classnames_exclude)

        if 'report' not in exclude and ph.user_can_edit_obj(self.request.user, obj):
            btns.append(
                self.report_button(pk, classnames_add, classnames_exclude)
            )
        return btns


class CreateExperimentView(CreateView):
    def form_valid(self, form):
        response = super(CreateExperimentView, self).form_valid(form)
        if form.instance.status == 'live':
            form.instance.activate_alternative_draft_content()
        return response


class EditExperimentView(EditView):
    def form_valid(self, form):
        response = super(EditExperimentView, self).form_valid(form)
        if self.instance._initial_status == 'draft' and self.instance.status == 'live':
            self.instance.activate_alternative_draft_content()

        return response


class ExperimentModelAdmin(ModelAdmin):
    model = Experiment
    add_to_settings_menu = True
    button_helper_class = ExperimentButtonHelper
    create_view_class = CreateExperimentView
    edit_view_class = EditExperimentView

modeladmin_register(ExperimentModelAdmin)


@hooks.register('before_serve_page')
def check_experiments(page, request, serve_args, serve_kwargs):
    # If the page being served is the goal page of an experiment, log a completion
    completed_experiments = Experiment.objects.filter(goal=page, status='live')

    if completed_experiments:
        user_id = get_user_id(request)

        for experiment in completed_experiments:
            experiment.record_completion_for_user(user_id, request)

    # If the page being served is the control page of an experiment, run the experiment
    experiments = Experiment.objects.filter(control_page=page, status__in=('live', 'completed'))
    if experiments:
        experiment = experiments[0]

        if experiment.status == 'completed' and experiment.winning_variation is not None:
            variation = experiment.winning_variation
        else:
            # always serve bots the control page
            ua_string = request.META.get('HTTP_USER_AGENT')
            if ua_string:
                ua = user_agents.parse(ua_string)
                if ua.is_bot:
                    return

            user_id = get_user_id(request)
            variation = experiment.start_experiment_for_user(user_id, request)

        if variation.pk != page.pk:
            # serve this alternative instead of the current page

            variation = variation.specific

            # hack the title and page-tree-related fields to match the control page
            impersonate_other_page(variation, page)

            return variation.serve(request, *serve_args, **serve_kwargs)
