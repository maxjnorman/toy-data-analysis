# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-11 16:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_app', '0008_auto_20161211_1612'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tableentry',
            name='table',
        ),
        migrations.DeleteModel(
            name='Table',
        ),
        migrations.DeleteModel(
            name='TableEntry',
        ),
    ]