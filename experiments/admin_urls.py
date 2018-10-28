from __future__ import absolute_import, unicode_literals

from django.urls import path
from experiments import views

app_name='experiments'

urlpatterns = [
    path('experiment/report/<int:experiment_id>/', views.experiment_report, name='report'),
    path('experiment/select_winner/<int:experiment_id>/<int:variation_id>/', views.select_winner, name='select_winner'),
    path('experiment/report/preview/<int:experiment_id>/<int:page_id>/', views.preview_for_report, name='preview_for_report'),
]
