# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0030_index_on_pagerevision_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alternative',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('control_page', models.ForeignKey(related_name='+', to='wagtailcore.Page')),
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
            field=models.ForeignKey(related_name='+', to='wagtailcore.Page'),
        ),
    ]
