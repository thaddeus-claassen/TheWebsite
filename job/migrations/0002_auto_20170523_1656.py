# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-23 21:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='num_people_doing_job',
            new_name='num_workers',
        ),
    ]