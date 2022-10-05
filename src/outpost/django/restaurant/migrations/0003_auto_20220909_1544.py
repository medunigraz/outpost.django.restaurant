# Generated by Django 2.2.26 on 2022-09-09 13:44

import django.contrib.postgres.fields
import django.contrib.postgres.fields.hstore
from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):

    dependencies = [
        ("restaurant", "0002_auto_20200805_1403"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="baseextractor",
            options={"base_manager_name": "objects"},
        ),
        migrations.AlterModelOptions(
            name="restaurant",
            options={"base_manager_name": "objects"},
        ),
        migrations.AlterModelOptions(
            name="xmlrestaurant",
            options={"base_manager_name": "objects"},
        ),
        migrations.AlterModelOptions(
            name="xsltextractor",
            options={"base_manager_name": "objects"},
        ),
        migrations.AddField(
            model_name="xmlrestaurant",
            name="decompose",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=256),
                blank=True,
                default=[],
                size=None,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="xmlrestaurant",
            name="headers",
            field=django.contrib.postgres.fields.hstore.HStoreField(
                blank=True, default={"Accept": "text/xml"}
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="xmlrestaurant",
            name="normalize",
            field=models.BooleanField(default=False),
        ),
    ]
