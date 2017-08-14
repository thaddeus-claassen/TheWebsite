# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-02 16:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0008_job_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='finished',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='job',
            name='workers',
            field=models.PositiveIntegerField(default=0),
        ),
    ]