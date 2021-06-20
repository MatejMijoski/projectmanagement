# Generated by Django 3.1.5 on 2021-05-07 21:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("ProjectManagementApp", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Files",
            fields=[
                ("file_id", models.AutoField(primary_key=True, serialize=False)),
                ("file_name", models.CharField(max_length=300)),
                ("file_size", models.IntegerField(verbose_name="File Size (Bytes)")),
                ("file_path", models.CharField(max_length=600)),
                ("file_uploaded_at", models.DateTimeField(auto_now=True)),
                (
                    "file_owner",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "project_files",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ProjectManagementApp.project",
                    ),
                ),
            ],
        ),
    ]
