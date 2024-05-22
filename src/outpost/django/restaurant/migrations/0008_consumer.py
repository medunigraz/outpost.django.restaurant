# Generated by Django 2.2.28 on 2024-05-07 08:23

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("restaurant", "0007_auto_20240426_1519"),
    ]

    operations = [
        migrations.CreateModel(
            name="Consumer",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                ("active", models.BooleanField(default=True)),
                (
                    "restaurants",
                    models.ManyToManyField(
                        related_name="consumers", to="restaurant.Restaurant"
                    ),
                ),
            ],
        ),
    ]