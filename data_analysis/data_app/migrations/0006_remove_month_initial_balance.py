# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-05 14:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_app', '0005_auto_20170204_2200'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='month',
            name='initial_balance',
        ),
    ]
