from __future__ import absolute_import, unicode_literals

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _

from wagtail.wagtailadmin import messages
from wagtail.wagtailcore.models import Page

from .models import Experiment, get_backend
from .utils import get_user_id, impersonate_other_page, percentage


def record_completion(request, slug):
    experiment = get_object_or_404(Experiment, slug=slug)
    user_id = get_user_id(request)

    experiment.record_completion_for_user(user_id, request)
    return HttpResponse("OK")


def experiment_report(request, experiment_id):
    # TODO: Decide if we need a custom permission to access reports

    backend = get_backend()
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    variations = experiment.get_variations()

    report = backend.get_report(experiment)

    report_by_variation = {}
    for variation in variations:
        for variation_report in report['variations']:
            if variation_report['variation_pk'] == variation.pk:
                if 'history' in variation_report:
                    for history_entry in variation_report['history']:
                        history_entry['conversion_rate'] = percentage(
                            history_entry['completion_count'],
                            history_entry['participant_count'],
                        )

                variation_report['total_conversion_rate'] = percentage(
                    variation_report['total_completion_count'],
                    variation_report['total_participant_count'],
                )
                report_by_variation[variation] = variation_report
                break

    return render(request, 'experiments/report.html', {
        'experiment': experiment,
        'report_by_variation': report_by_variation,
        'winning_variation': experiment.winning_variation if experiment.status == 'completed' else None,
    })


def select_winner(request, experiment_id, variation_id):
    if not request.user.has_perm('experiments.change_experiment'):
        raise PermissionDenied
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    variation = get_object_or_404(Page, pk=variation_id)

    if request.method == 'POST':
        experiment.select_winner(variation)

        messages.success(
            request,
            _("Page '{0}' has been selected as the winning variation.").format(variation.title),
        )

    return redirect('experiments:report', experiment.pk)


def preview_for_report(request, experiment_id, page_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    page = get_object_or_404(Page, id=page_id).specific
    if not page.permissions_for_user(request.user).can_publish():
        raise PermissionDenied

    # hack the title and page-tree-related fields to match the control page
    impersonate_other_page(page, experiment.control_page)

    # pass in the real user request rather than page.dummy_request(), so that request.user
    # and request.revision_id will be picked up by the wagtail user bar
    return page.serve_preview(request, page.default_preview_mode)
