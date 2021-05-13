from django.contrib import admin

# Register your models here.
from SlackApp.models import Slack_Auth, WSS_Auth

admin.site.register(Slack_Auth)
admin.site.register(WSS_Auth)
