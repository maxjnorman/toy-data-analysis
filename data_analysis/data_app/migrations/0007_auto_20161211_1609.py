# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-11 16:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_app', '0006_auto_20161211_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='heading_balance',
            field=models.CharField(default='Account Balance', max_length=50),
        ),
        migrations.AlterField(
            model_name='account',
            name='heading_date',
            field=models.CharField(default='Transaction Date', max_length=50),
        ),
        migrations.AlterField(
            model_name='account',
            name='heading_description',
            field=models.CharField(default='Description', max_length=50),
        ),
        migrations.AlterField(
            model_name='account',
            name='heading_in',
            field=models.CharField(default='Money In', max_length=50),
        ),
        migrations.AlterField(
            model_name='account',
            name='heading_out',
            field=models.CharField(default='Money Out', max_length=50),
        ),
    ]
