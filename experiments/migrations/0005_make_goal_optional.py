# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0004_add_completed_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='goal',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, related_name='+', to='wagtailcore.Page'),
        ),
    ]
