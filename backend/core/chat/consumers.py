import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
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
        
        from ..models import Room, Message

        room = await database_sync_to_async(Room.objects.get)(
            host__slug=self.username,
            slug=self.room_slug
        )
        
        # Check if the user is a participant in the room
        if not await database_sync_to_async(room.participants.filter(id=self.user.id).exists)():
            await self.send(text_data=json.dumps({"error": "You are not a participant in this room."}))
            return

        if message_type == 'text':
            message_body = data.get('message')
            await self.handle_new_message(room, message_body)
        
        elif message_type == 'delete':
            message_id = data.get('messageId')
            await self.handle_delete_message(message_id)

        elif message_type == 'update':
            message_id = data.get('messageId')
            new_body = data.get('message')
            await self.handle_update_message(message_id, new_body)

    async def handle_new_message(self, room, message_body):
        """Handle creation of a new message"""
        from ..models import Message
        
        new_message = await database_sync_to_async(Message.objects.create)(
            user=self.user,
            room=room,
            body=message_body
        )
        
        serialized_message = new_message.serialize()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',  # Event type handled by `chat_message`
                'action': 'new',
                **serialized_message,
            }
        )

    async def handle_delete_message(self, message_id):
        """Handle deletion of a message"""
        from ..models import Message
        
        try:
            @database_sync_to_async
            def get_message():
                return Message.objects.get(id=message_id)
            
            @database_sync_to_async
            def check_ownership(message):
                return str(message.user.id) == str(self.user.id)
                
            @database_sync_to_async
            def delete_message(message):
                message.delete()
            
            message = await get_message()
            
            if not await check_ownership(message):
                await self.send(text_data=json.dumps({"error": "You can only delete your own messages."}))
                return
            
            await delete_message(message)
            
            # Broadcast the deletion to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'delete',
                    'id': message_id
                }
            )
        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"Failed to delete message: {str(e)}"}))

    async def handle_update_message(self, message_id, new_body):
        """Handle updating a message"""
        from ..models import Message
        
        try:
            @database_sync_to_async
            def get_message():
                return Message.objects.get(id=message_id)
            
            @database_sync_to_async
            def check_ownership(message: Message):
                return str(message.user.id) == str(self.user.id)
                
            @database_sync_to_async
            def update_message(message: Message):
                message.update(new_body)
                return message.updated
            
            message = await get_message()
            
            if not await check_ownership(message):
                await self.send(text_data=json.dumps({"error": "You can only edit your own messages."}))
                return
            
            updated_timestamp = await update_message(message)
            
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
        except Exception as e:
            await self.send(text_data=json.dumps({"error": f"Failed to update message: {str(e)}"}))

    async def chat_message(self, event):
        """
        Handle broadcasted messages and send them to WebSocket clients.
        """
        await self.send(text_data=json.dumps(event))
        