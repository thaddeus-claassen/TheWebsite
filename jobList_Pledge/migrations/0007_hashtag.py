# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-06 18:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobList_Pledge', '0006_auto_20160827_1734'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hashtag', models.CharField(max_length=30)),
                ('jobs', models.ManyToManyField(to='jobList_Pledge.Job')),
            ],
        ),
    ]
