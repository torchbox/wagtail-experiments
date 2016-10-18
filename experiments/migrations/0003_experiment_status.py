# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0002_experiment_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='status',
            field=models.CharField(default='draft', choices=[('draft', 'Draft'), ('live', 'Live')], max_length=10),
        ),
    ]
