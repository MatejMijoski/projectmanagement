import urllib
import uuid

import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
import json
from rest_framework.authtoken.models import Token
from AuthenticationApp.models import Account
from projectmanagement import settings
from SlackApp.models import Slack_Auth, WSS_Auth
from django.contrib.auth import hashers
from rest_framework.response import Response


# TODO
# 1. Get all conversations
# https://slack.com/api/conversations.list
# 2. REFACTOR CODE

# Create your views here.
@api_view(http_method_names=["GET"])
@authentication_classes([])
@permission_classes([])
def slack_signup(request):
    response = requests.get(
        "https://slack.com/api/oauth.v2.access?client_id="
        + settings.client_id
        + "&client_secret="
        + settings.client_secret
        + "&code="
        + request.GET.get("code", "")
        + "&redirect_uri="
        + urllib.parse.quote("http://localhost:8000/api/auth/slack/callback")
    )
    json_response = json.loads(response.content)

    # Continue only if this is true
    if json_response["ok"]:
        responseEmail = requests.get(
            "https://slack.com/api/users.identity",
            headers={
                "Authorization": "Bearer "
                + json_response["authed_user"]["access_token"]
            },
        )
        emailJson = json.loads(responseEmail.content)

        try:
            Slack_Auth.objects.get(user_id=json_response["authed_user"]["id"])
            return Response(status=404)
        except Slack_Auth.DoesNotExist:
            account = Account.objects.create(
                email=emailJson["user"]["email"],
                password=hashers.make_password(None),
                email_verified=True,
            )
            slack_account = Slack_Auth.objects.create(
                user_id=json_response["authed_user"]["id"],
                access_token=json_response["authed_user"]["access_token"],
                team_id=json_response["team"]["id"],
                slack_account=account,
            )

            token = Token.objects.create(user=account)
            return JsonResponse(
                data={
                    "slack_user_id": slack_account.slack_id,
                    "user_id": slack_account.user_id,
                    "token": getattr(token, "key"),
                },
                status=200,
            )
    return Response(status=404)


@api_view(http_method_names=["GET"])
@authentication_classes([])
@csrf_exempt
@permission_classes([])
def slack_signin(request):
    data = json.loads(request.data)
    try:
        slack_account = Slack_Auth.objects.get(
            slack_id=data["slack_user_id"], user_id=data["user_id"]
        )
        token = Token.objects.create(user=slack_account.slack_account)
        return JsonResponse(data={"token": token}, status=200)
    except Slack_Auth.DoesNotExist:
        return Response(status=404)


# https://slack.com/oauth/v2/authorize?user_scope=identity.basic,identity.email&client_id=1733891928675.1733932256451&redirect_uri=http://localhost:8000/api/auth/slack/callback
# https://slack.com/oauth/v2/authorize?user_scope=channels:history,chat:write&client_id=1733891928675.1733932256451&redirect_uri=http://localhost:8000/api/slack/permissions/callback

# Add to Slack view
@api_view(http_method_names=["GET"])
@authentication_classes([])
@permission_classes([])
def slack_authorization(request):
    response = requests.get(
        "https://slack.com/api/oauth.v2.access?client_id="
        + settings.client_id
        + "&client_secret="
        + settings.client_secret
        + "&code="
        + request.GET.get("code", "")
        + "&redirect_uri="
        + urllib.parse.quote("http://localhost:8000/api/slack/permissions/callback")
    )
    json_response = json.loads(response.content)
    # Continue only if this is true
    if json_response["ok"]:
        return Response(status=200)
    else:
        return Response(status=400)


# https://slack.com/oauth/v2/authorize?user_scope=channels:history,channels:read,chat:write&client_id=1733891928675.1733932256451&redirect_uri=http://localhost:8000/api/slack/permissions/callback

# Get all channels, send slack_user_id and user_id to find if the user has permissions.
@api_view(http_method_names=["POST"])
@csrf_exempt
def get_slack_channels(request):
    data = request.data
    try:
        user = Slack_Auth.objects.get(
            slack_account=request.user,
            slack_id=data["slack_user_id"],
            user_id=data["user_id"],
        )
        response = requests.get(
            "https://slack.com/api/conversations.list",
            headers={"Authorization": "Bearer " + user.access_token},
        )
        try:
            token = WSS_Auth.objects.create(user=request.user, user_uid=uuid.uuid4())
            jsonResp = json.loads(response.content)
            channels = {}
            for channel in jsonResp["channels"]:
                channels.update({channel["id"]: channel["name"]})
            channels.update({"ws-token": token.user_uid})
            return Response(data=json.dumps(channels), status=200)
        except IntegrityError:
            token = WSS_Auth.objects.get(user=request.user)
            jsonResp = json.loads(response.content)
            channels = {}
            for channel in jsonResp["channels"]:
                channels.update({channel["id"]: channel["name"]})
            channels.update({"ws-token": token.user_uid})
            return Response(data=json.dumps(channels), status=200)

    except Slack_Auth.DoesNotExist:
        return Response(status=404)


@api_view(http_method_names=["POST"])
@authentication_classes([])
@permission_classes([])
@csrf_exempt
def slack_events(request):
    # Check for validity
    if request.data["token"] == settings.SLACK_VERIFICATION_TOKEN:
        channel_layer = get_channel_layer()

        # Updated message doesn't have event object so check if the message was sent or updated
        # Deleted file returns only "ok"
        if request.data["event"]["channel"]:
            try:
                if request.data["event"]["text"]:
                    group_name = "channel_{}".format(request.data["event"]["channel"])
                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            "type": "send_message",
                            "message": request.data["event"]["text"],
                        },
                    )
            except KeyError:
                pass
        elif request.data["channel"]:
            group_name = "channel_{}".format(request.data["channel"])
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_message",
                    "message": request.data["text"],
                },
            )
    return Response(data=request.data, status=200)
    # return Response(data=request.data["challenge"], status=200)


@api_view(http_method_names=["GET"])
@csrf_exempt
def slack_pagination(request):
    if (
        request.GET.get("cursor", "") != ""
        and request.GET.get("channel-id", "") != ""
        and request.GET.get("user-id", "") != ""
    ):
        try:
            user = Slack_Auth.objects.get(
                slack_account=request.user, user_id=request.GET.get("user-id", "")
            )
            response = requests.get(
                "https://slack.com/api/conversations.history?channel="
                + request.GET.get("channel-id", "")
                + "cursor="
                + request.GET.get("cursor", ""),
                headers={"Authorization": "Bearer " + user.access_token},
            )
            return Response(data=json.loads(response.content), status=200)
        except Slack_Auth.DoesNotExist:
            pass


# Edited message isn't returned by the Events API so get the new message from the response and change it
# TODO Limit the number of characters for new and updated messages
@api_view(http_method_names=["POST"])
@csrf_exempt
def slack_update_message(request):
    data = json.loads(request.data)
    if data["ts"] != "" and data["updated_message"] != "" and data["channel-id"] != "":
        try:
            user = Slack_Auth.objects.get(slack_account=request.user)
            response = requests.post(
                "https://slack.com/api/chat.update",
                data={
                    "channel": data["channel-id"],
                    "ts": data["ts"],
                    "text": data["updated_message"],
                },
                headers={"Authorization": "Bearer " + user.access_token},
            )
            responseJson = json.loads(response.content)
            if responseJson["ok"]:
                return Response(data=json.dumps(response.content), status=200)
            elif responseJson["error"] == "message_not_found":
                return JsonResponse(
                    data={"error": "The message doesn't exist."}, status=400
                )
            elif responseJson["error"] == "cant_update_message":
                return JsonResponse(
                    data={"error": "You don't have permissions to edit this message."},
                    status=400,
                )
            elif responseJson["error"] == "update_failed":
                return JsonResponse(
                    data={
                        "error": "The Slack server is not available. Please try again later"
                    },
                    status=500,
                )
            elif responseJson["error"] == "msg_too_long":
                return JsonResponse(
                    data={"error": "The message is too long"}, status=400
                )
            else:
                return JsonResponse(
                    data={
                        "error": "The message can not be updated. Please try again later or"
                        "try the Slack App."
                    },
                    status=500,
                )
        except Slack_Auth.DoesNotExist:
            return Response(status=404)
    return Response(status=400)


@api_view(http_method_names=["GET"])
@csrf_exempt
def slack_delete_message(request, channel_id):
    if request.GET.get("ts", "") != "":
        try:
            user = Slack_Auth.objects.get(slack_account=request.user)
            response = requests.post(
                "https://slack.com/api/chat.delete",
                data={"channel": channel_id, "ts": request.GET.get("ts", "")},
                headers={"Authorization": "Bearer " + user.access_token},
            )
            data = json.loads(response.content)
            if data["ok"]:
                return Response(data=response.content, status=200)
            else:
                return Response(
                    data=json.dumps({"data": "The message was not found"}), status=404
                )
        except Slack_Auth.DoesNotExist:
            return Response(status=404)
    return Response(status=400)


@api_view(http_method_names=["POST"])
@csrf_exempt
def slack_file_upload(request, channel_id):
    files = request.FILES.getlist("file")
    if files:
        try:
            user = Slack_Auth.objects.get(slack_account=request.user)
            uploaded_files = []
            for file in files:
                response = requests.post(
                    "https://slack.com/api/files.upload",
                    files={"file": file},
                    data={"channels": channel_id},
                    headers={"Authorization": "Bearer " + user.access_token},
                )
                responseJson = json.loads(response.content.decode("UTF-8"))
                if not responseJson["ok"]:
                    if responseJson["error"] == "posting_to_general_channel_denied":
                        responseJson.update(
                            {"error": "The admin has restricted posting."}
                        )
                    elif responseJson["error"] == "invalid_channel":
                        responseJson.update({"error": "The channel is not valid."})
                    elif (
                        responseJson["error"]
                        == "slack_connect_file_upload_sharing_blocked"
                    ):
                        responseJson.update(
                            {"error": "The admin has restricted file uploads."}
                        )
                    else:
                        responseJson.update(
                            {
                                "error": "The message can not be updated. Please try again later or"
                                "try the Slack App."
                            }
                        )
                uploaded_files.append(responseJson)
            return Response(data=json.dumps({"data": uploaded_files}), status=200)
        except Slack_Auth.DoesNotExist:
            return Response(status=404)
    return Response(status=400)


# If the status is 200, remove the file from the chat
@api_view(http_method_names=["POST"])
@csrf_exempt
def slack_file_delete(request):
    data = json.loads(request.data)
    try:
        user = Slack_Auth.objects.get(slack_account=request.user)
        deleted_files = []
        for file in data["file"]:
            response = requests.post(
                "https://slack.com/api/files.delete",
                data={"file": file},
                headers={"Authorization": "Bearer " + user.access_token},
            )
            responseJson = json.loads(response.content.decode("UTF-8"))
            try:
                if responseJson["error"] == "file_deleted":
                    responseJson.update({"error": "The file has already been deleted."})
                deleted_files.append(responseJson)
            except KeyError:
                pass
        return Response(data=json.dumps({"data": deleted_files}), status=200)
    except Slack_Auth.DoesNotExist:
        return Response(status=404)
