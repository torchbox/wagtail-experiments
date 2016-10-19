# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0030_index_on_pagerevision_created_at'),
        ('experiments', '0003_experiment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='winning_variation',
            field=models.ForeignKey(to='wagtailcore.Page', on_delete=django.db.models.deletion.SET_NULL, null=True, related_name='+'),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='status',
            field=models.CharField(default='draft', choices=[('draft', 'Draft'), ('live', 'Live'), ('completed', 'Completed')], max_length=10),
        ),
    ]
