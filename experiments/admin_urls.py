from django.urls import re_path
from experiments import views

app_name = 'experiments'

urlpatterns = [
    re_path(r'^experiment/report/(\d+)/$', views.experiment_report, name='report'),
    re_path(r'^experiment/select_winner/(\d+)/(\d+)/$', views.select_winner, name='select_winner'),
    re_path(r'^experiment/report/preview/(\d+)/(\d+)/$', views.preview_for_report, name='preview_for_report'),
]
