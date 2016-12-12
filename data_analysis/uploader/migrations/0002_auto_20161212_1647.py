# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-12 16:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='upload',
            name='pic',
        ),
        migrations.AddField(
            model_name='upload',
            name='docfile',
            field=models.FileField(default='dpc', upload_to='documents/', verbose_name='Document'),
            preserve_default=False,
        ),
    ]
