.. image:: wagtail-experiments.png

Wagtail Experiments
===================

A/B testing for Wagtail

Installation
------------

Add ``'experiments'`` to ``INSTALLED_APPS``.

Direct URLs for goal completion
-------------------------------

If you want goal completion to be linked to some action other than visiting a designated Wagtail page - for example, clicking a 'follow us on Twitter' link - you can set up a Javascript action that sends a request to a URL such as ``/experiments/complete/twitter-follow/`` , where ``twitter-follow`` is the experiment slug. To set this URL route up, add the following to your URLconf:

.. code-block:: python

    from experiments import views as experiment_views

    urlpatterns = [
        # ...

        url(r'^experiments/complete/([^\/]+)/$', experiment_views.record_completion),

        # ...
    ]
