# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-26 02:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_auto_20180925_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='cost',
            field=models.FloatField(default=0, verbose_name='Cost'),
        ),
        migrations.AddField(
            model_name='item',
            name='cost_updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
