from __future__ import absolute_import, unicode_literals

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Experiment
from .utils import get_user_id


def record_completion(request, slug):
    experiment = get_object_or_404(Experiment, slug=slug)
    user_id = get_user_id(request)

    experiment.record_completion_for_user(user_id, request)
    return HttpResponse("OK")
