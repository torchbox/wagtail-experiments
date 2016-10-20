from __future__ import absolute_import, unicode_literals

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Experiment, get_backend
from .utils import get_user_id, percentage


def record_completion(request, slug):
    experiment = get_object_or_404(Experiment, slug=slug)
    user_id = get_user_id(request)

    experiment.record_completion_for_user(user_id, request)
    return HttpResponse("OK")


def experiment_report(request, pk):
    # TODO: Decide if we need a custom permission to access reports

    backend = get_backend()
    experiment = get_object_or_404(Experiment, pk=pk)
    variations = experiment.get_variations()

    report = backend.get_report(experiment)

    report_by_variation = {}
    for variation in variations:
        for variation_report in report['variations']:
            if variation_report['variation_pk'] == variation.pk:
                if 'history' in variation_report:
                    for history_entry in variation_report['history']:
                        history_entry['conversions_rate'] = percentage(
                            history_entry['completion_count'],
                            history_entry['participant_count'],
                        )

                variation_report['total_conversions_rate'] = percentage(
                    variation_report['total_completion_count'],
                    variation_report['total_participant_count'],
                )
                report_by_variation[variation] = variation_report
                break

    return render(request, 'experiments/report.html', {
        'experiment': experiment,
        'report_by_variation': report_by_variation,
    })
