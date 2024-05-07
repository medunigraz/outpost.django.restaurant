# Generated by Django 2.2.28 on 2024-05-07 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
        ("restaurant", "0008_consumer"),
    ]

    operations = [
        migrations.AddField(
            model_name="restaurant",
            name="consumers",
            field=models.ManyToManyField(
                related_name="_restaurant_consumers_+", to="api.Consumer"
            ),
        ),
        migrations.DeleteModel(
            name="Consumer",
        ),
    ]
