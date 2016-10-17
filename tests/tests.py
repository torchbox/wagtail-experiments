from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from wagtail.wagtailcore.models import Page

from experiments.models import Experiment, ExperimentHistory


class TestIndexView(TestCase):
    fixtures = ['test.json']

    def setUp(self):
        self.experiment = Experiment.objects.get(slug='homepage-text')
        self.homepage = Page.objects.get(url_path='/home/')
        self.homepage_alternative_1 = Page.objects.get(url_path='/home/home-alternative-1/')
        self.homepage_alternative_2 = Page.objects.get(url_path='/home/home-alternative-2/')

        # Results obtained experimentally:
        # User ID 11111111-1111-1111-1111-111111111111 receives the control version of the homepage
        # User ID 22222222-2222-2222-2222-222222222222 also receives the control
        # User ID 33333333-3333-3333-3333-333333333333 receives alternative 1

    def test_user_is_assigned_user_id(self):
        session = self.client.session
        self.assertNotIn('experiment_user_id', session)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        session = self.client.session
        self.assertIn('experiment_user_id', session)

    def test_selected_variation_depends_on_user_id(self):
        session = self.client.session
        session['experiment_user_id'] = '11111111-1111-1111-1111-111111111111'
        session.save()

        for x in range(0, 5):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<p>Welcome to our site!</p>')

        session['experiment_user_id'] = '33333333-3333-3333-3333-333333333333'
        session.save()

        for x in range(0, 5):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<p>Welcome to our site! It&#39;s lovely to meet you.</p>')

    def test_participant_is_logged(self):
        # initially there should be no experiment history
        self.assertEqual(ExperimentHistory.objects.filter(experiment=self.experiment).count(), 0)

        # User 11111111-1111-1111-1111-111111111111
        session = self.client.session
        session['experiment_user_id'] = '11111111-1111-1111-1111-111111111111'
        session.save()
        self.client.get('/')

        # there should be one history record
        self.assertEqual(ExperimentHistory.objects.filter(experiment=self.experiment).count(), 1)
        history_record = ExperimentHistory.objects.get(
            experiment=self.experiment, variation=self.homepage
        )
        self.assertEqual(history_record.participant_count, 1)

        # User 22222222-2222-2222-2222-222222222222
        session = self.client.session
        session['experiment_user_id'] = '22222222-2222-2222-2222-222222222222'
        session.save()
        self.client.get('/')

        # this should update the existing record
        self.assertEqual(ExperimentHistory.objects.filter(experiment=self.experiment).count(), 1)
        history_record = ExperimentHistory.objects.get(
            experiment=self.experiment, variation=self.homepage
        )
        self.assertEqual(history_record.participant_count, 2)

        # User 33333333-3333-3333-3333-333333333333
        session = self.client.session
        session['experiment_user_id'] = '33333333-3333-3333-3333-333333333333'
        session.save()
        self.client.get('/')

        # this should create a new record, for alternative 1
        self.assertEqual(ExperimentHistory.objects.filter(experiment=self.experiment).count(), 2)
        history_record = ExperimentHistory.objects.get(
            experiment=self.experiment, variation=self.homepage_alternative_1
        )
        self.assertEqual(history_record.participant_count, 1)

    def test_completion_is_logged(self):
        # User 11111111-1111-1111-1111-111111111111
        session = self.client.session
        session['experiment_user_id'] = '11111111-1111-1111-1111-111111111111'
        session.save()
        self.client.get('/')

        # history record should show 1 participant, 0 completions
        history_record = ExperimentHistory.objects.get(
            experiment=self.experiment, variation=self.homepage
        )
        self.assertEqual(history_record.participant_count, 1)
        self.assertEqual(history_record.completion_count, 0)

        self.client.get('/signup-complete/')

        # history record should show 1 participant, 1 completion
        history_record = ExperimentHistory.objects.get(
            experiment=self.experiment, variation=self.homepage
        )
        self.assertEqual(history_record.participant_count, 1)
        self.assertEqual(history_record.completion_count, 1)
