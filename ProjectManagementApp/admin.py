from django.contrib import admin
from ProjectManagementApp.models import Project, Client, PostComments, Invoice, Resume, \
    TimelineItemClient, ClientAddress, ProjectPosts, ProjectInvites

admin.site.register(Project)
admin.site.register(ClientAddress)
admin.site.register(Client)
admin.site.register(ProjectPosts)
admin.site.register(ProjectInvites)
admin.site.register(PostComments)
admin.site.register(Invoice)
admin.site.register(Resume)
admin.site.register(TimelineItemClient)
