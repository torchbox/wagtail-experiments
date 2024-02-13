# Generated by Django 4.2.4 on 2024-02-12 21:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0005_make_goal_optional"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="alternative",
            options={
                "ordering": ["sort_order"],
                "verbose_name": "alternative",
                "verbose_name_plural": "alternatives",
            },
        ),
        migrations.AlterModelOptions(
            name="experiment",
            options={
                "verbose_name": "experiment",
                "verbose_name_plural": "experiments",
            },
        ),
        migrations.AlterModelOptions(
            name="experimenthistory",
            options={
                "verbose_name": "experiment history",
                "verbose_name_plural": "experiment histories",
            },
        ),
    ]