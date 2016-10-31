from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from wagtail.wagtailcore.models import Page

from experiments.models import Experiment, ExperimentHistory


class TestFrontEndView(TestCase):
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

        session.clear()
        session['experiment_user_id'] = '33333333-3333-3333-3333-333333333333'
        session.save()

        for x in range(0, 5):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<p>Welcome to our site! It&#39;s lovely to meet you.</p>')

    def test_bot_user_agent_gets_control_page(self):
        session = self.client.session

        # non-bot user agent string
        for x in range(0, 5):
            session.clear()
            session['experiment_user_id'] = '33333333-3333-3333-3333-333333333333'
            session.save()
            response = self.client.get('/', HTTP_USER_AGENT="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0")
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<p>Welcome to our site! It&#39;s lovely to meet you.</p>')

        # bot user agent string
        for x in range(0, 5):
            session.clear()
            session['experiment_user_id'] = '33333333-3333-3333-3333-333333333333'
            session.save()
            response = self.client.get('/', HTTP_USER_AGENT="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)")
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<p>Welcome to our site!</p>')

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
        session.clear()
        session['experiment_user_id'] = '22222222-2222-2222-2222-222222222222'
        session.save()
        self.client.get('/')

        # this should update the existing record
        self.assertEqual(ExperimentHistory.objects.filter(experiment=self.experiment).count(), 1)
        history_record = ExperimentHistory.objects.get(
            experiment=self.experiment, variation=self.homepage
        )
        self.assertEqual(history_record.participant_count, 2)

        # repeated requests from the same user should not update the count
        self.client.get('/')
        self.assertEqual(ExperimentHistory.objects.filter(experiment=self.experiment).count(), 1)
        history_record = ExperimentHistory.objects.get(
            experiment=self.experiment, variation=self.homepage
        )
        self.assertEqual(history_record.participant_count, 2)

        # User 33333333-3333-3333-3333-333333333333
        session.clear()
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

        # repeated completions from the same user should not update the count
        self.client.get('/signup-complete/')
        history_record = ExperimentHistory.objects.get(
            experiment=self.experiment, variation=self.homepage
        )
        self.assertEqual(history_record.participant_count, 1)
        self.assertEqual(history_record.completion_count, 1)

    def test_completion_is_not_counted_if_experiment_not_started(self):
        session = self.client.session
        session['experiment_user_id'] = '11111111-1111-1111-1111-111111111111'
        session.save()
        self.client.get('/signup-complete/')

        # this user went directly to the goal page without participating in the experiment,
        # so there should be no participation or completion records
        self.assertEqual(ExperimentHistory.objects.filter(experiment=self.experiment).count(), 0)

    def test_completion_through_direct_url(self):
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

        self.client.get('/experiments/complete/homepage-text/')

        # history record should show 1 participant, 1 completion
        history_record = ExperimentHistory.objects.get(
            experiment=self.experiment, variation=self.homepage
        )
        self.assertEqual(history_record.participant_count, 1)
        self.assertEqual(history_record.completion_count, 1)

        # repeated completions from the same user should not update the count
        self.client.get('/experiments/complete/homepage-text/')
        history_record = ExperimentHistory.objects.get(
            experiment=self.experiment, variation=self.homepage
        )
        self.assertEqual(history_record.participant_count, 1)
        self.assertEqual(history_record.completion_count, 1)

    def test_completion_through_direct_url_is_not_counted_if_experiment_not_started(self):
        session = self.client.session
        session['experiment_user_id'] = '11111111-1111-1111-1111-111111111111'
        session.save()
        self.client.get('/experiments/complete/homepage-text/')

        # this user went directly to the goal page without participating in the experiment,
        # so there should be no participation or completion records
        self.assertEqual(ExperimentHistory.objects.filter(experiment=self.experiment).count(), 0)

    def test_draft_status(self):
        self.experiment.status = 'draft'
        self.experiment.save()

        session = self.client.session
        session['experiment_user_id'] = '33333333-3333-3333-3333-333333333333'
        session.save()
        response = self.client.get('/')

        # User 33333333-3333-3333-3333-333333333333 would get alternative 1 when the experiment is live,
        # but should get the standard homepage when it's draft
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<p>Welcome to our site!</p>')

        # no participant record should be logged
        self.assertEqual(ExperimentHistory.objects.filter(experiment=self.experiment).count(), 0)

        # completions should not be logged either
        self.client.get('/signup-complete/')
        self.assertEqual(ExperimentHistory.objects.filter(experiment=self.experiment).count(), 0)

    def test_original_title_is_preserved(self):
        session = self.client.session
        session['experiment_user_id'] = '11111111-1111-1111-1111-111111111111'
        session.save()
        response = self.client.get('/')
        self.assertContains(response, "<title>Home</title>")

        # User receiving an alternative version should see the title as "Home", not "Homepage alternative 1"
        session.clear()
        session['experiment_user_id'] = '33333333-3333-3333-3333-333333333333'
        session.save()
        response = self.client.get('/')
        self.assertContains(response, "<title>Home</title>")

    def test_original_tree_position_is_preserved(self):
        # Alternate version should position itself in the tree as if it were the control page
        session = self.client.session
        session['experiment_user_id'] = '33333333-3333-3333-3333-333333333333'
        session.save()
        response = self.client.get('/')
        self.assertContains(response, '<li class="current">Home</li>')

    def test_completed_status(self):
        self.experiment.status = 'completed'
        self.experiment.winning_variation = self.homepage_alternative_2
        self.experiment.save()

        # all users should be served the winning variation

        session = self.client.session
        session['experiment_user_id'] = '11111111-1111-1111-1111-111111111111'
        session.save()
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<p>Oh, it&#39;s you. What do you want?</p>")


class TestAdmin(TestCase):
    fixtures = ['test.json']

    def setUp(self):
        User.objects.create_superuser(username='admin', email='admin@example.com', password='password')
        self.assertTrue(
            self.client.login(username='admin', password='password')
        )
        self.experiment = Experiment.objects.get(slug='homepage-text')
        self.homepage = Page.objects.get(url_path='/home/').specific
        self.homepage_alternative_1 = Page.objects.get(url_path='/home/home-alternative-1/').specific
        self.homepage_alternative_2 = Page.objects.get(url_path='/home/home-alternative-2/').specific

    def get_edit_postdata(self, **kwargs):
        alternatives = self.experiment.alternatives.all()

        postdata = {
            'name': self.experiment.name,
            'slug': self.experiment.slug,
            'control_page': self.experiment.control_page.pk,
            'alternatives-TOTAL_FORMS': 2,
            'alternatives-INITIAL_FORMS': 2,
            'alternatives-MIN_NUM_FORMS': 0,
            'alternatives-MAX_NUM_FORMS': 1000,

            'alternatives-0-page': alternatives[0].page.pk,
            'alternatives-0-id': alternatives[0].pk,
            'alternatives-0-ORDER': '1',
            'alternatives-0-DELETE': '',

            'alternatives-1-page': alternatives[1].page.pk,
            'alternatives-1-id': alternatives[1].pk,
            'alternatives-1-ORDER': '2',
            'alternatives-1-DELETE': '',

            'goal': self.experiment.goal.pk,
            'status': self.experiment.status,
        }
        postdata.update(kwargs)
        return postdata

    def test_experiments_menu_item(self):
        response = self.client.get(reverse('wagtailadmin_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/admin/experiments/experiment/"')

    def test_experiments_index(self):
        response = self.client.get('/admin/experiments/experiment/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Homepage text')

    def test_experiment_new(self):
        response = self.client.get('/admin/experiments/experiment/create/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/admin/experiments/experiment/create/', {
            'name': "Another experiment",
            'slug': 'another-experiment',
            'control_page': self.homepage_alternative_1.pk,
            'alternatives-TOTAL_FORMS': 1,
            'alternatives-INITIAL_FORMS': 0,
            'alternatives-MIN_NUM_FORMS': 0,
            'alternatives-MAX_NUM_FORMS': 1000,
            'alternatives-0-page': self.homepage_alternative_2.pk,
            'alternatives-0-id': '',
            'alternatives-0-ORDER': '1',
            'alternatives-0-DELETE': '',
            'goal': self.homepage.pk,
            'status': 'draft',
        })
        self.assertRedirects(response, '/admin/experiments/experiment/')
        self.assertTrue(Experiment.objects.filter(slug='another-experiment').exists())

    def test_experiment_edit(self):
        response = self.client.get('/admin/experiments/experiment/edit/%d/' % self.experiment.pk)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/admin/experiments/experiment/edit/%d/' % self.experiment.pk,
            self.get_edit_postdata(name="Homepage text updated")
        )
        self.assertRedirects(response, '/admin/experiments/experiment/')
        experiment = Experiment.objects.get(pk=self.experiment.pk)
        self.assertEqual(experiment.name, "Homepage text updated")

    def test_draft_page_content_is_activated_when_experiment_goes_live(self):
        # make a draft edit to homepage_alternative_1
        self.homepage_alternative_1.body = 'updated'
        self.homepage_alternative_1.save_revision()

        # live database entry should not have been updated yet
        homepage_alternative_1 = Page.objects.get(pk=self.homepage_alternative_1.pk).specific
        self.assertEqual(homepage_alternative_1.body, "Welcome to our site! It's lovely to meet you.")

        # submit an edit to the experiment, but preserve its live status
        self.client.post(
            '/admin/experiments/experiment/edit/%d/' % self.experiment.pk,
            self.get_edit_postdata()
        )
        # editing an already-live experiment should not update the page content
        homepage_alternative_1 = Page.objects.get(pk=self.homepage_alternative_1.pk).specific
        self.assertEqual(homepage_alternative_1.body, "Welcome to our site! It's lovely to meet you.")

        # make the experiment draft
        self.client.post(
            '/admin/experiments/experiment/edit/%d/' % self.experiment.pk,
            self.get_edit_postdata(status='draft')
        )
        # page content should still be unchanged
        homepage_alternative_1 = Page.objects.get(pk=self.homepage_alternative_1.pk).specific
        self.assertEqual(homepage_alternative_1.body, "Welcome to our site! It's lovely to meet you.")

        # set the experiment from draft to live
        self.client.post(
            '/admin/experiments/experiment/edit/%d/' % self.experiment.pk,
            self.get_edit_postdata(status='live')
        )
        # page content should be updated to follow the draft revision now
        homepage_alternative_1 = Page.objects.get(pk=self.homepage_alternative_1.pk).specific
        self.assertEqual(homepage_alternative_1.body, 'updated')

    def test_draft_page_content_is_activated_when_creating_experiment_as_live(self):
        # make a draft edit to homepage_alternative_1
        self.homepage_alternative_1.body = 'updated'
        self.homepage_alternative_1.save_revision()

        # create a new experiment with an immediate live status
        response = self.client.post('/admin/experiments/experiment/create/', {
            'name': "Another experiment",
            'slug': 'another-experiment',
            'control_page': self.homepage.pk,
            'alternatives-TOTAL_FORMS': 1,
            'alternatives-INITIAL_FORMS': 0,
            'alternatives-MIN_NUM_FORMS': 0,
            'alternatives-MAX_NUM_FORMS': 1000,
            'alternatives-0-page': self.homepage_alternative_1.pk,
            'alternatives-0-id': '',
            'alternatives-0-ORDER': '1',
            'alternatives-0-DELETE': '',
            'goal': '',
            'status': 'live',
        })

        self.assertRedirects(response, '/admin/experiments/experiment/')

        # page content should be updated to follow the draft revision now
        homepage_alternative_1 = Page.objects.get(pk=self.homepage_alternative_1.pk).specific
        self.assertEqual(homepage_alternative_1.body, 'updated')

    def test_draft_page_content_is_not_activated_on_published_pages(self):
        # publish homepage_alternative_1
        self.homepage_alternative_1.save_revision().publish()

        # make a draft edit to homepage_alternative_1
        self.homepage_alternative_1.body = 'updated'
        self.homepage_alternative_1.save_revision()

        # make the experiment draft
        self.client.post(
            '/admin/experiments/experiment/edit/%d/' % self.experiment.pk,
            self.get_edit_postdata(status='draft')
        )
        # set the experiment from draft to live
        self.client.post(
            '/admin/experiments/experiment/edit/%d/' % self.experiment.pk,
            self.get_edit_postdata(status='live')
        )

        # page content should still be unchanged
        homepage_alternative_1 = Page.objects.get(pk=self.homepage_alternative_1.pk).specific
        self.assertEqual(homepage_alternative_1.body, "Welcome to our site! It's lovely to meet you.")

    def test_draft_page_content_is_not_activated_on_published_pages_when_creating_experiment_as_live(self):
        # publish homepage_alternative_1
        self.homepage_alternative_1.save_revision().publish()

        # make a draft edit to homepage_alternative_1
        self.homepage_alternative_1.body = 'updated'
        self.homepage_alternative_1.save_revision()

        # create a new experiment with an immediate live status
        response = self.client.post('/admin/experiments/experiment/create/', {
            'name': "Another experiment",
            'slug': 'another-experiment',
            'control_page': self.homepage.pk,
            'alternatives-TOTAL_FORMS': 1,
            'alternatives-INITIAL_FORMS': 0,
            'alternatives-MIN_NUM_FORMS': 0,
            'alternatives-MAX_NUM_FORMS': 1000,
            'alternatives-0-page': self.homepage_alternative_1.pk,
            'alternatives-0-id': '',
            'alternatives-0-ORDER': '1',
            'alternatives-0-DELETE': '',
            'goal': '',
            'status': 'live',
        })

        self.assertRedirects(response, '/admin/experiments/experiment/')

        # page content should still be unchanged
        homepage_alternative_1 = Page.objects.get(pk=self.homepage_alternative_1.pk).specific
        self.assertEqual(homepage_alternative_1.body, "Welcome to our site! It's lovely to meet you.")

    def test_experiment_delete(self):
        response = self.client.get('/admin/experiments/experiment/delete/%d/' % self.experiment.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure you want to delete this experiment?")

        response = self.client.post('/admin/experiments/experiment/delete/%d/' % self.experiment.pk)
        self.assertRedirects(response, '/admin/experiments/experiment/')
        self.assertFalse(Experiment.objects.filter(slug='homepage-text').exists())

    def test_show_report(self):
        response = self.client.get('/admin/experiments/experiment/report/%d/' % self.experiment.pk)
        self.assertEqual(response.status_code, 200)

    def test_select_winner(self):
        response = self.client.post(
            '/admin/experiments/experiment/select_winner/%d/%d/' % (
                self.experiment.pk, self.homepage_alternative_1.pk
            )
        )
        self.assertRedirects(
            response,
            '/admin/experiments/experiment/report/%d/' % self.experiment.pk
        )
        experiment = Experiment.objects.get(pk=self.experiment.pk)
        self.assertEqual(experiment.status, 'completed')
        self.assertEqual(experiment.winning_variation.pk, self.homepage_alternative_1.pk)

    def test_preview(self):
        response = self.client.get(
            '/admin/experiments/experiment/report/preview/%d/%d/' % (
                self.experiment.pk, self.homepage_alternative_1.pk
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<title>Home</title>")
