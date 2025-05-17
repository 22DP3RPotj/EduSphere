import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError


class ChatConsumer(AsyncWebsocketConsumer):
    @property
    def max_body_length(self):
        """
        Return the maximum length of the message body.
        """
        from ..models import Message
        return Message._meta.get_field("body").max_length

    async def send_error(self, error_message):
        """
        Send an error message to the WebSocket client.
        """
        payload = {"error": error_message}
        await self.send(text_data=json.dumps(payload))

    async def connect(self):
        """
        Authenticate user, verify room exists and that the user is a participant,
        then add to group and accept the WebSocket connection.
        """
        user = self.scope.get('user')

        if not user or not user.is_authenticated:
            await self.close()
            return
        
        self.user = user

        self.username = self.scope['url_route']['kwargs']['username']
        self.room_slug = self.scope['url_route']['kwargs']['room']
        self.room_group_name = f'chat_{self.username}_{self.room_slug}'


        from ..models import Room
        try:
            room = await database_sync_to_async(Room.objects.get)(
                host__username=self.username,
                slug=self.room_slug
            )
        except Room.DoesNotExist:
            await self.close()
            return

        is_participant = await database_sync_to_async(
            room.participants.filter(id=self.user.id).exists
        )()
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """
        Leave the room group on disconnect.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Handle incoming messages: text, delete, or update.
        Assumes only participants reach this point.
        """
        data = json.loads(text_data)
        message_type = data.get('type', 'text')


        from ..models import Room
        room = await database_sync_to_async(Room.objects.get)(
            host__username=self.username,
            slug=self.room_slug
        )

        if message_type == 'text':
            await self.handle_new_message(room, data.get('message'))

        elif message_type == 'delete':
            await self.handle__delete_message(data.get('messageId'))

        elif message_type == 'update':
            await self.handle_update_message(
                data.get('messageId'),
                data.get('message')
            )

    async def handle_new_message(self, room, message_body):
        """Handle creation of a new message"""
        from ..models import Message

        @database_sync_to_async
        def create_message(user, room, body):
            message = Message(user=user, room=room, body=body)
            message.full_clean()
            message.save()
            return message

        try:
            new_message = await create_message(
                user=self.user,
                room=room,
                body=message_body
            )
        except ValidationError:
            await self.send_error(
                f"Message exceeds {self.max_body_length} characters."
            )
            return

        serialized = new_message.serialize()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'action': 'new',
                **serialized,
            }
        )

    async def handle__delete_message(self, message_id):
        """Handle deletion of a message"""
        from ..models import Message

        @database_sync_to_async
        def get_message():
            return Message.objects.get(id=message_id)
        @database_sync_to_async
        def check_owner(message):
            return message.user_id == self.user.id
        @database_sync_to_async
        def delete_message(message):
            message.delete()

        try:
            message = await get_message()
        except Message.DoesNotExist:
            await self.send_error("Message not found.")
            return

        if not await check_owner(message):
            await self.send_error("You can only delete your own messages.")
            return

        await delete_message(message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'action': 'delete',
                'id': message_id,
            }
        )

    async def handle_update_message(self, message_id, new_body):
        """Handle updating a message"""
        from ..models import Message

        @database_sync_to_async
        def get_message():
            return Message.objects.get(id=message_id)
        @database_sync_to_async
        def check_owner(message):
            return message.user_id == self.user.id
        @database_sync_to_async
        def do_update(message):
            message.update(new_body)
            return message.updated

        try:
            message = await get_message()
        except Message.DoesNotExist:
            await self.send_error("Message not found.")
            return

        if not await check_owner(message):
            await self.send_error("You can only edit your own messages.")
            return

        try:
            updated_ts = await do_update(message)
        except ValidationError:
            await self.send_error(
                f"Message exceeds {self.max_body_length} characters."
            )
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'action': 'update',
                'id': message_id,
                'body': new_body,
                'edited': True,
                'updated': updated_ts.isoformat() if updated_ts else None,
            }
        )

    async def chat_message(self, event):
        """
        Receive messages sent to the group and relay to WebSocket clients.
        """
        await self.send(text_data=json.dumps(event))
