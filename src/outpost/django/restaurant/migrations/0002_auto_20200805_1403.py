# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-08-05 12:03
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):

    dependencies = [
        ("restaurant", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="meal",
            name="diet",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="restaurant.Diet",
            ),
        ),
    ]
