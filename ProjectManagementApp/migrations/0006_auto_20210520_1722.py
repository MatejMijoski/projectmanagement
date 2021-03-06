# Generated by Django 3.1.5 on 2021-05-20 15:22

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ProjectManagementApp", "0005_auto_20210516_2248"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectInvite",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                        verbose_name="Invite ID",
                    ),
                ),
                (
                    "email",
                    models.CharField(max_length=150, verbose_name="Invite Email"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now=True, verbose_name="Created At"),
                ),
                (
                    "expire_at",
                    models.DateTimeField(
                        default=datetime.datetime(2021, 5, 30, 17, 22, 44, 358653),
                        verbose_name="Created At",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invites",
                        to="ProjectManagementApp.project",
                        verbose_name="Project Invite",
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sender",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Invite Sender",
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="ProjectInvites",
        ),
    ]
