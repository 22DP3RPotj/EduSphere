import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract slugs from the WebSocket URL
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_slug = self.scope['url_route']['kwargs']['room']
        
        self.room_group_name = f'chat_{self.username}_{self.room_slug}'

        # Add the WebSocket connection to the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the WebSocket connection from the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages, save them to the database, and broadcast to the group.
        """
        # Parse the incoming WebSocket data
        data = json.loads(text_data)
        message_body = data.get('message')  # The message text
        user = self.scope['user']  # The currently authenticated user
        
        from .models import Room, Message

        # Save the message to the database
        room = await database_sync_to_async(Room.objects.get)(
            host__slug=self.username,
            slug=self.room_slug
        )
        
        new_message = await database_sync_to_async(Message.objects.create)(
            user=user,
            room=room,
            body=message_body
        )

        # Prepare the serialized message data
        serialized_message = {
            'id': str(new_message.id),
            'user': user.username,
            'user_id': user.id,
            'user_avatar': user.avatar.url,
            'message': new_message.body,
            'created': new_message.created.strftime('%Y-%m-%d %H:%M:%S'),
        }

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',  # Event type handled by `chat_message`
                **serialized_message,
            }
        )

    async def chat_message(self, event):
        """
        Handle broadcasted messages and send them to WebSocket clients.
        """
        # Send the broadcasted message to the WebSocket client
        await self.send(text_data=json.dumps(event))
