# Generated by Django 2.1.2 on 2018-10-28 20:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0002_simplepagerelatedlink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simplepage',
            name='page_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page'),
        ),
    ]