# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0030_index_on_pagerevision_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='SimplePage',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, parent_link=True, to='wagtailcore.Page', auto_created=True, serialize=False)),
                ('body', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
