import json

import requests
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from SlackApp.models import WSS_Auth, Slack_Auth


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print('da')
        try:
            # Get the channel ID from request
            self.user_uid = self.scope['query_string'].decode("UTF-8").split("=")[1]
            self.channel_id = self.scope['url_route']['kwargs']['channel_id']
            # TODO A check for if the user can listen to the channel might be needed
            # TODO Get all of the channels for the user and compare the channel ID
            # Create a room for that channel
            self.channel_group = 'channel_{}'.format(self.channel_id)
            try:
                user = WSS_Auth.objects.get(user_uid=self.user_uid)
                self.user_acc = user.user
                user.delete()

                # Join channel group i.e add the user to the group of channels
                async_to_sync(self.channel_layer.group_add)(
                    self.channel_group,
                    self.channel_name
                )
                self.accept()

                # Get previous messages from Slack and return after accepting
                user = Slack_Auth.objects.get(slack_account=self.user_acc)
                response = requests.get(
                    'https://slack.com/api/conversations.history?channel=' + self.channel_id,
                    headers={"Authorization": "Bearer " + user.access_token})
                self.send(text_data=json.dumps(response.content.decode('UTF-8')))
            except WSS_Auth.DoesNotExist:
                pass
        except KeyError:
            pass

    def disconnect(self, close_code):
        # Leave Slack channel group
        async_to_sync(self.channel_layer.group_discard)(
            self.channel_group,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        #  Send text_data to Slack server as user
        user = Slack_Auth.objects.get(slack_account=self.user_acc)
        response = requests.post(
            'https://slack.com/api/chat.postMessage',data={"channel": self.channel_id, "text": text_data},
            headers={"Authorization": "Bearer " + user.access_token})

    def send_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps(
            message))
