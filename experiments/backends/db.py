from __future__ import absolute_import, unicode_literals

import datetime

from django.db.models import F

from experiments.models import ExperimentHistory


def record_participant(experiment, user_id, variation):
    # get or create a History record for this experiment variation and the current date
    history, _ = ExperimentHistory.objects.get_or_create(
        experiment=experiment, variation=variation, date=datetime.date.today()
    )
    # increment the participant_count
    ExperimentHistory.objects.filter(pk=history.pk).update(participant_count=F('participant_count') + 1)


def record_completion(experiment, user_id, variation):
    # get or create a History record for this experiment variation and the current date
    history, _ = ExperimentHistory.objects.get_or_create(
        experiment=experiment, variation=variation, date=datetime.date.today()
    )
    # increment the completion_count
    ExperimentHistory.objects.filter(pk=history.pk).update(completion_count=F('completion_count') + 1)
