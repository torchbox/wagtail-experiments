from __future__ import absolute_import, unicode_literals

from django.urls import include, path, re_path

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls

from experiments import views as experiment_views


urlpatterns = [
    path('admin/', include(wagtailadmin_urls)),

    re_path(r'^experiments/complete/([^\/]+)/$', experiment_views.record_completion),

    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's serving mechanism
    path('', include(wagtail_urls)),
]
