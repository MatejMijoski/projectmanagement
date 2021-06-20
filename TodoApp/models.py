from django.db import models
from AuthenticationApp.models import Account
import uuid
from ProjectManagementApp.models import Project


# Create your models here.
class ProjectTasks(models.Model):
    TASK_TYPE = (
        ("NOT_STARTED", "Not Started"),
        ("IN_PROGRESS", "In Progress"),
        ("DONE", "Done"),
    )

    TASK_IMPORTANCE = (("HIGH", "High"), ("MEDIUM", "Medium"), ("LOW", "Low"))

    objects: models.Manager
    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="Resume ID",
        primary_key=True,
    )
    owner = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="tasks", verbose_name="Owner"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_tasks",
        verbose_name="Project",
    )
    type = models.CharField(
        choices=TASK_TYPE, max_length=20, blank=False, default=None, verbose_name="Type"
    )
    importance = models.CharField(
        choices=TASK_IMPORTANCE,
        max_length=20,
        blank=False,
        default=None,
        verbose_name="Importance",
    )
    title = models.TextField(verbose_name="Title")
    is_completed = models.BooleanField(
        default=False, null=False, verbose_name="Is Completed"
    )
    description = models.TextField(verbose_name="Description")
    due_date = models.DateTimeField(verbose_name="Due Date")
    created_at = models.DateTimeField(auto_now=True, verbose_name="Created At")
