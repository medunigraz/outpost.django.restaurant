# Generated by Django 2.2.28 on 2023-09-19 09:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("restaurant", "0003_auto_20220909_1544"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="restaurant",
            options={"ordering": ("name",)},
        ),
    ]