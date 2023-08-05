
from django.urls import include, re_path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls

from experiments import views as experiment_views


urlpatterns = [
    re_path(r'^admin/', include(wagtailadmin_urls)),

    re_path(r'^experiments/complete/([^\/]+)/$', experiment_views.record_completion),

    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's serving mechanism
    re_path(r'', include(wagtail_urls)),
]
