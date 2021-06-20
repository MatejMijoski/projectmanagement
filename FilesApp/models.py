import uuid

from django.db import models
from AuthenticationApp.models import Account
from ProjectManagementApp.models import Project


# Create your models here.
class Files(models.Model):
    objects: models.Manager
    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="File ID",
        primary_key=True,
    )
    name = models.CharField(max_length=300, verbose_name="File Name")
    owner = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="files",
        verbose_name="File Owner",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_files",
        verbose_name="Project",
    )
    size = models.IntegerField(verbose_name="File Size (Bytes)")
    path = models.CharField(max_length=600, verbose_name="Path")
    created_at = models.DateTimeField(auto_now=True)
