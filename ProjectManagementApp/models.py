import uuid
from datetime import timedelta, datetime
from django.db import models
from django.db.models import JSONField
from AuthenticationApp.models import Account


class Client(models.Model):
    objects: models.Manager
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="Client ID", primary_key=True
    )
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name="Client Owner")
    name = models.CharField(max_length=200, blank=False, verbose_name="Client Name")
    email = models.EmailField(null=True, verbose_name="Client Email")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Client Phone")
    company = models.CharField(max_length=150, blank=True, verbose_name='Client Company')
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['owner', 'email'], name='Client Constraint'),
        ]


class ClientAddress(models.Model):
    objects: models.Manager
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="Client Address ID", primary_key=True
    )
    country = models.CharField(max_length=150, blank=True, verbose_name="Country")
    state = models.CharField(max_length=80, verbose_name="State", blank=True)
    city = models.CharField(max_length=80, blank=True, verbose_name="City")
    zip_code = models.CharField(max_length=30, blank=True, verbose_name="Zip Code")
    client = models.OneToOneField(
        Client,
        on_delete=models.CASCADE,
        verbose_name="Client",
        related_name="client_address",
    )


class Project(models.Model):
    objects: models.Manager
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="Project ID", primary_key=True
    )
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='project_owner',
                              verbose_name='Project Owner')
    users = models.ManyToManyField(Account, null=True, related_name='project_clients', verbose_name='Project Users')
    name = models.CharField(max_length=100, blank=False, verbose_name='Project Name')
    description = models.CharField(max_length=1000, blank=True, verbose_name='Project Description')
    clients = models.ManyToManyField(Client, null=True, related_name='client_projects', verbose_name='Project Clients')
    time = models.IntegerField(null=True, verbose_name='Project Time')
    budget = models.IntegerField(default=0, verbose_name='Project Budget')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Created At')
    due_date = models.DateTimeField(null=True, verbose_name='Project Due Date')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'owner'], name='Project Name Constraint'),
        ]


class ProjectInvites(models.Model):
    objects: models.Manager
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="Invite ID", primary_key=True
    )
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="sender", verbose_name="Invite Sender")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="invites",
                                verbose_name="Project Invite")
    email = models.CharField(max_length=150, blank=False, null=False, verbose_name="Invite Email")
    created_at = models.DateTimeField(auto_now=True, verbose_name='Created At')
    expire_at = models.DateTimeField(default=datetime.now() + timedelta(days=10), verbose_name='Created At')

    def add_user(self, user):
        self.project.users.add(user)
        self.project.save()
        self.delete()
        return True


class ProjectPosts(models.Model):
    TYPE_CHOICES = (
        ('BUG', 'Bug'),
        ('QUESTION', 'Question'),
        ("NOTE", "Note")
    )

    objects: models.Manager
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="Post ID", primary_key=True
    )
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='post_owner', null=False,
                              verbose_name='Post Owner')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='post_project', null=False,
                                verbose_name='Post Project')
    content = models.TextField(max_length=1000, blank=False, verbose_name='Post Content')
    type = models.CharField(choices=TYPE_CHOICES, blank=False, max_length=20, verbose_name='Post Type')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Created At')


class PostComments(models.Model):
    objects: models.Manager
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="Comment ID", primary_key=True
    )
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='comment_owner', null=False,
                              verbose_name='Owner')
    post = models.ForeignKey(ProjectPosts, on_delete=models.CASCADE, related_name='comment_post', null=False,
                             verbose_name='Comment Post')
    content = models.TextField(max_length=1000, verbose_name='Comment Content')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Created At')


class Invoice(models.Model):
    objects: models.Manager()
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="Invoice ID", primary_key=True
    )
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name="Owner")
    name_surname = models.CharField(max_length=100, verbose_name="Name and Surname")
    email = models.CharField(max_length=100, verbose_name='Email')
    address = models.CharField(max_length=100, blank=True, verbose_name="Address")
    company_name = models.CharField(max_length=100, blank=True, verbose_name="Company Name")
    phone = models.CharField(max_length=100, blank=True, verbose_name="Phone")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, verbose_name="Client")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, verbose_name="Project")
    number = models.IntegerField(default=1, verbose_name="Invoice Number")
    due_date = models.DateTimeField(null=True, verbose_name="Due Date")
    items = JSONField(verbose_name="Invoice Items")
    total = models.FloatField(verbose_name="Invoice Total")
    is_paid = models.BooleanField(default=False, verbose_name="Is Invoice Paid")
    note = models.TextField(default="", verbose_name="Invoice Note")
    terms = models.TextField(default="", verbose_name="Invoice Terms")
    created_at = models.DateTimeField(auto_now=True, verbose_name="Created At")


class Resume(models.Model):
    objects: models.Manager()
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="Resume ID", primary_key=True
    )
    owner = models.OneToOneField(Account, related_name="user_resume", on_delete=models.CASCADE)
    name = models.CharField(max_length=150, default="", blank=True, verbose_name="Name and Surname")
    position = models.CharField(max_length=250, default="", blank=True, verbose_name="Position")
    description = models.TextField(default="", blank=True, verbose_name="Description")
    languages = JSONField(default=dict(), blank=True, verbose_name="Languages")
    skills = JSONField(default=dict(), blank=True, verbose_name="Skills")
    education = JSONField(default=dict(), blank=True, verbose_name="Education")
    work_experience = JSONField(default=dict(), blank=True, verbose_name="Work Experience")
    certificates = JSONField(default=dict(), blank=True, verbose_name="Certificates")
    achievements = JSONField(default=dict(), blank=True, verbose_name="Achievements")
    personal_projects = JSONField(default=dict(), blank=True, verbose_name="Personal Projects")
    contact_info = JSONField(default=dict(), blank=True, verbose_name="Contact Info")


class TimelineItemClient(models.Model):
    ITEM_IMPORTANCE = (
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low')
    )

    objects: models.Manager
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="Resume ID", primary_key=True
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='timeline_items', verbose_name="Clients")
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='client_timeline_items', verbose_name="Owner")
    importance = models.CharField(choices=ITEM_IMPORTANCE, max_length=20, default="LOW", null=False, verbose_name="Importance")
    title = models.CharField(max_length=150, verbose_name="Title")
    description = models.CharField(max_length=1000, verbose_name="Description")
    date = models.DateTimeField(verbose_name="Date")
    created_at = models.DateTimeField(auto_now=True)

