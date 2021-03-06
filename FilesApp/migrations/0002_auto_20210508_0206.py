# Generated by Django 3.1.5 on 2021-05-08 00:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ProjectManagementApp", "0003_auto_20210508_0206"),
        ("FilesApp", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="files",
            old_name="file_uploaded_at",
            new_name="created_at",
        ),
        migrations.RenameField(
            model_name="files",
            old_name="file_size",
            new_name="size",
        ),
        migrations.RemoveField(
            model_name="files",
            name="file_id",
        ),
        migrations.RemoveField(
            model_name="files",
            name="file_name",
        ),
        migrations.RemoveField(
            model_name="files",
            name="file_owner",
        ),
        migrations.RemoveField(
            model_name="files",
            name="file_path",
        ),
        migrations.RemoveField(
            model_name="files",
            name="project_files",
        ),
        migrations.AddField(
            model_name="files",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                primary_key=True,
                serialize=False,
                unique=True,
                verbose_name="File ID",
            ),
        ),
        migrations.AddField(
            model_name="files",
            name="name",
            field=models.CharField(
                default="name", max_length=300, verbose_name="File Name"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="files",
            name="owner",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="files",
                to="AuthenticationApp.account",
                verbose_name="File Owner",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="files",
            name="path",
            field=models.CharField(default="path", max_length=600, verbose_name="Path"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="files",
            name="project",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="project_files",
                to="ProjectManagementApp.project",
                verbose_name="Project",
            ),
            preserve_default=False,
        ),
    ]
