# Generated by Django 4.2.5 on 2023-12-28 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_photo_user"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
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
                ("title", models.CharField(max_length=20)),
            ],
        ),
    ]
