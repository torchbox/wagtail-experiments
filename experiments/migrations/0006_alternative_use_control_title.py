# Generated by Django 4.1.9 on 2023-07-04 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0005_make_goal_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='alternative',
            name='use_control_title',
            field=models.BooleanField(default=True),
        ),
    ]
