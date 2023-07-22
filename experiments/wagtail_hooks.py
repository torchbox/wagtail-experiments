from __future__ import absolute_import, unicode_literals

from django.urls import include, re_path
from django.contrib.admin.utils import quote

try:
    from django.urls import reverse
except ImportError:  # fallback for Django <=1.9
    from django.core.urlresolvers import reverse

from django.utils.translation import gettext_lazy as _
from experiments import admin_urls
from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.modeladmin.views import CreateView, EditView

try:
    from wagtail import hooks
except ImportError:  # fallback for Wagtail <5.0
    try:
        from wagtail.core import hooks
    except ImportError:  # fallback for Wagtail <2.0
        from wagtail.wagtailcore import hooks

from .models import Experiment
from .utils import get_user_id, impersonate_other_page, use_control_title


@hooks.register('register_admin_urls')
def register_admin_urls():
    '''
        Register a wagtail hook for the admin urls.

        Args:
            None

        Return:
            A list of url paths for experiments.
    '''
    return [
        re_path(r'^experiments/', include(admin_urls, namespace='experiments')),
    ]


class ExperimentButtonHelper(ButtonHelper):
    '''
        Define the helper button for an experiment.
    '''
    def report_button(self, pk, classnames_add=[], classnames_exclude=[]):
        '''
            Get the report button.

            Args:
                self:                instance of the class ExperimentButtonHelper
                pk:                  the primary key for the experiment.
                classnames_add:      a list of classnames to include; defaults to empty list.
                classnames_exclude:  a list of to exclude; defaults to empty list.

            Return:
                A list of url paths for experiments.
        '''
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
        '''
            Get the wagtail button to generate a report.

            Args:
                self:                instance of the class ExperimentButtonHelper
                obj:                 the primary key for the experiment.
                exclude:             a list to exclude inspect, edit, and/or delete; defaults to empty list.
                classnames_add:      a list of classnames to include; defaults to empty list.
                classnames_exclude:  a list of to exclude; defaults to empty list.

            Return:
                A list of url paths for experiments.
        '''
        ph = self.permission_helper
        pk = quote(getattr(obj, self.opts.pk.attname))
        btns = super(ExperimentButtonHelper, self).get_buttons_for_obj(obj, exclude, classnames_add, classnames_exclude)

        if 'report' not in exclude and ph.user_can_edit_obj(self.request.user, obj):
            btns.append(
                self.report_button(pk, classnames_add, classnames_exclude)
            )
        return btns


class CreateExperimentView(CreateView):
    '''
        Define the Create view for an experiment.
    '''
    def form_valid(self, form):
        '''
            Check the form is valid. If the form's status is "live",
            then the alternative draft content is activated.

            Args:
                self:  instance of the class CreateExperimentView
                form:  form to validate.

            Return:
                A django HttpResponse whether the form is valid.
        '''
        response = super(CreateExperimentView, self).form_valid(form)
        if form.instance.status == 'live':
            form.instance.activate_alternative_draft_content()
        return response


class EditExperimentView(EditView):
    '''
        Define the Edit view for an experiment.
    '''
    def form_valid(self, form):
        '''
            Check the form is valid. If the form's status is "live",
            then the alternative draft content is activated.

            Args:
                self:  instance of the class CreateExperimentView
                form:  form to validate.

            Return:
                A django HttpResponse whether the form is valid.
        '''
        response = super(EditExperimentView, self).form_valid(form)
        if self.instance._initial_status == 'draft' and self.instance.status == 'live':
            self.instance.activate_alternative_draft_content()

        return response


class ExperimentModelAdmin(ModelAdmin):
    '''
        Define the admin model for an Experiment.
    '''
    model = Experiment
    add_to_settings_menu = True
    button_helper_class = ExperimentButtonHelper
    create_view_class = CreateExperimentView
    edit_view_class = EditExperimentView

modeladmin_register(ExperimentModelAdmin)


@hooks.register('before_serve_page')
def check_experiments(page, request, serve_args, serve_kwargs):
    '''
        Check whether the page is a control or goal of an experiment.
        If the page is a control page, run the experiment.
        If the page is a goal page, log a completion.

        Args:
            page:          page being served.
            request:       django HttpRequest.
            serve_args:    non-keyword arguments for page being served.
            serve_kwargs:  keyword arguments for the page being served

        Return:
            If the page is a control page in a live, yet uncompleted, experiment
            and the variation page for this user is not the same as the page,
            then show the variation page. Otherwise, return nothing.
    '''
    
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
            user_id = get_user_id(request)
            variation = experiment.start_experiment_for_user(user_id, request)

        if variation.pk != page.pk:
            # serve this alternative instead of the current page

            variation = variation.specific

            use_title = use_control_title(experiment, variation)

            # hack the page-tree-related fields to match the control page
            impersonate_other_page(variation, page, use_title)

            return variation.serve(request, *serve_args, **serve_kwargs)
