from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from experiments import views

urlpatterns = [
    url(r'^experiment/report/(\d+)/$', views.experiment_report, name='report'),
    url(r'^experiment/select_winner/(\d+)/(\d+)/$', views.select_winner, name='select_winner'),
    url(r'^experiment/report/preview/(\d+)/(\d+)/$', views.preview_for_report, name='preview_for_report'),
]
