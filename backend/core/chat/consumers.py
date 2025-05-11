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
        user = self.scope.get('user')
        
        if not user or not user.is_authenticated:
            await self.close()
            return

        self.user = user
        
        # Extract slugs from the WebSocket URL
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_slug = self.scope['url_route']['kwargs']['room']
        
        self.room_group_name = f'chat_{self.username}_{self.room_slug}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # await self.send(text_data=json.dumps({
        #     "type": "meta",
        #     "maxBodyLength": self.max_body_length,
        # }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages, save them to the database, and broadcast to the group.
        """
        data = json.loads(text_data)
        message_type = data.get('type', 'text')
        
        from ..models import Room

        try:
            room = await database_sync_to_async(Room.objects.get)(
                host__slug=self.username,
                slug=self.room_slug
            )
        except Room.DoesNotExist:
            await self.send_error("Room not found.")
            return
        
        if not await database_sync_to_async(room.participants.filter(id=self.user.id).exists)():
            await self.send_error("You are not a participant in this room.")
            return

        if message_type == 'text':
            message_body = data.get('message')
            await self.handle_new_message(room, message_body)
        
        elif message_type == 'delete':
            message_id = data.get('messageId')
            await self.handle__delete_message(message_id)

        elif message_type == 'update':
            message_id = data.get('messageId')
            new_body = data.get('message')
            await self.handle_update_message(message_id, new_body)

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
            await self.send_error(f"Message exceeds {self.max_body_length} characters.")
            return
        
        serialized_message = new_message.serialize()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'action': 'new',
                **serialized_message,
            }
        )

    async def handle__delete_message(self, message_id):
        """Handle deletion of a message"""
        from ..models import Message
        
        @database_sync_to_async
        def _get_message():
            return Message.objects.get(id=message_id)
        
        @database_sync_to_async
        def _check_ownership(message):
            return str(message.user.id) == str(self.user.id)
            
        @database_sync_to_async
        def _delete_message(message):
            message.delete()
            
        try:
            message = await _get_message()
        except Message.DoesNotExist:
            await self.send_error("Message not found.")
            return
            
        if not await _check_ownership(message):
            await self.send_error("You can only delete your own messages.")
            return
        
        await _delete_message(message)
        
        # Broadcast the deletion to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'action': 'delete',
                'id': message_id
            }
        )

    async def handle_update_message(self, message_id, new_body):
        """Handle updating a message"""
        from ..models import Message
        
        @database_sync_to_async
        def _get_message():
            return Message.objects.get(id=message_id)
        
        @database_sync_to_async
        def _check_ownership(message: Message):
            return str(message.user.id) == str(self.user.id)
            
        @database_sync_to_async
        def update_message(message: Message):
            message.update(new_body)
            return message.updated
        
        try:
            message = await _get_message()
        except Message.DoesNotExist:
            await self.send_error("Message not found.")
            return
            
        if not await _check_ownership(message):
            await self.send_error("You can only edit your own messages.")
            return
        
        try:
            updated_timestamp = await update_message(message)
        except ValidationError:
            await self.send_error(f"Message exceeds {self.max_body_length} characters.")
            return
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'action': 'update',
                'id': message_id,
                'body': new_body,
                'edited': True,
                'updated': updated_timestamp.isoformat() if updated_timestamp else None
            }
        )

    async def chat_message(self, event):
        """
        Handle broadcasted messages and send them to WebSocket clients.
        """
        await self.send(text_data=json.dumps(event))
        