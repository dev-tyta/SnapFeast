# Generated by Django 5.0.3 on 2024-06-28 17:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MealOrder",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "food_type",
                    models.CharField(
                        choices=[
                            ("CHOICE1", "Amala"),
                            ("CHOICE2", "Choice 2"),
                            ("CHOICE3", "Choice 3"),
                        ],
                        max_length=10,
                    ),
                ),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("date_ordered", models.DateTimeField(auto_now_add=True)),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
