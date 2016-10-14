from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Experiment


class ExperimentModelAdmin(ModelAdmin):
    model = Experiment
    add_to_settings_menu = True

modeladmin_register(ExperimentModelAdmin)
