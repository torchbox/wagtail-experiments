# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import modelcluster.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0030_index_on_pagerevision_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alternative',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('sort_order', models.IntegerField(null=True, blank=True, editable=False)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('control_page', models.ForeignKey(related_name='+', to='wagtailcore.Page', on_delete=django.db.models.deletion.SET_NULL)),
                ('goal', models.ForeignKey(related_name='+', to='wagtailcore.Page', on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='alternative',
            name='experiment',
            field=modelcluster.fields.ParentalKey(related_name='alternatives', to='experiments.Experiment'),
        ),
        migrations.AddField(
            model_name='alternative',
            name='page',
            field=models.ForeignKey(related_name='+', to='wagtailcore.Page', on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
