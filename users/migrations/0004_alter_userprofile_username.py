# Generated by Django 5.0.3 on 2024-06-29 20:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_alter_userprofile_age"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="username",
            field=models.CharField(max_length=200, null=True, unique=True),
        ),
    ]
