from django.db import models
import uuid
from AuthenticationApp.models import Account


# Create your models here.
class Lead(models.Model):
    objects: models.Manager
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="Lead ID", primary_key=True
    )
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='leads', verbose_name="Lead Owner")
    name = models.CharField(max_length=150, verbose_name="Lead Name")
    address = models.CharField(max_length=600, verbose_name="Lead Address")
    email = models.EmailField(null=True, verbose_name="Lead Email")
    phone = models.IntegerField(null=True, verbose_name="Lead Phone")
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['owner', 'email'], name='Lead Constraint'),
        ]


class TimelineItemLead(models.Model):
    objects: models.Manager
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="Timeline Lead Item ID", primary_key=True
    )
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='timeline_items', verbose_name="Lead")
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='lead_timeline_items', verbose_name="Item Owner")
    title = models.CharField(max_length=150, verbose_name="Title")
    description = models.CharField(max_length=1000, verbose_name="Description")
    date = models.DateTimeField(verbose_name="Date")
    created_at = models.DateTimeField(auto_now=True)
