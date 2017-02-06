# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-05 22:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('data_app', '0006_remove_month_initial_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='month',
            name='initial_balance',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='created_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='account',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='month',
            name='month_date',
            field=models.DateField(),
        ),
    ]
