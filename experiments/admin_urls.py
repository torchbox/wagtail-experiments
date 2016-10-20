from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from experiments import views

urlpatterns = [
    url(r'^experiment/report/(\d+)/$', views.experiment_report, name='experiments_experiment_modeladmin_report'),
]
