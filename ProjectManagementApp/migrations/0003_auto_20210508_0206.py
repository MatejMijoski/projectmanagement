# Generated by Django 3.1.5 on 2021-05-08 00:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ProjectManagementApp", "0002_auto_20210508_0024"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projectinvites",
            name="expire_at",
            field=models.DateTimeField(
                default=datetime.datetime(2021, 5, 18, 2, 6, 9, 270702),
                verbose_name="Created At",
            ),
        ),
    ]
