# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-02 16:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobuser', '0014_auto_20170715_1758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pay',
            name='amount',
            field=models.FloatField(blank=True, editable=False, null=True),
        ),
    ]