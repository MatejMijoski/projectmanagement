from django.urls import path
from SlackApp import views

urlpatterns = [
    path("auth/slack/callback", views.slack_signup),
    path("auth/slack/sign_in", views.slack_signin),
    path("slack/permissions/callback", views.slack_authorization),
    path("slack/channels", views.get_slack_channels),
    path("slack/events", views.slack_events),
    path("slack/update_message", views.slack_update_message),
    path("slack/delete_message/<str:channel_id>/", views.slack_delete_message),
    path("slack/upload_file/<str:channel_id>", views.slack_file_upload),
    path("slack/delete_file", views.slack_file_delete),
]
