# Generated by Django 3.1.5 on 2021-05-07 22:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ProjectManagementApp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projectinvites",
            name="expire_at",
            field=models.DateTimeField(
                default=datetime.datetime(2021, 5, 18, 0, 24, 54, 492620),
                verbose_name="Created At",
            ),
        ),
    ]
