# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0030_index_on_pagerevision_created_at'),
        ('experiments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExperimentHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('participant_count', models.PositiveIntegerField(default=0)),
                ('completion_count', models.PositiveIntegerField(default=0)),
                ('experiment', models.ForeignKey(to='experiments.Experiment', related_name='history', on_delete=django.db.models.deletion.SET_NULL)),
                ('variation', models.ForeignKey(to='wagtailcore.Page', related_name='+', on_delete=django.db.models.deletion.SET_NULL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='experimenthistory',
            unique_together=set([('experiment', 'date', 'variation')]),
        ),
    ]
