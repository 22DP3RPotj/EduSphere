import json
import redis
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = redis.Redis(
            host=getattr(settings, 'REDIS_HOST', 'localhost'),
            port=getattr(settings, 'REDIS_PORT', 6379),
            db=getattr(settings, 'REDIS_DB', 0),
            decode_responses=True
        )
        self.consumer_group = None
        self.consumer_name = None
        self.stream_key = None

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

        # Redis Streams setup
        self.stream_key = f"chat_stream:{self.username}:{self.room_slug}"
        self.consumer_group = f"chat_group:{self.username}:{self.room_slug}"
        self.consumer_name = f"consumer:{self.user.id}:{self.channel_name}"

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

        # Setup Redis Streams consumer group
        await self.setup_redis_streams()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Start consuming from Redis Streams
        asyncio.create_task(self.consume_stream_messages())

    async def setup_redis_streams(self):
        """Setup Redis Streams consumer group"""
        try:
            # Create consumer group if it doesn't exist
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.redis_client.xgroup_create(
                    self.stream_key, 
                    self.consumer_group, 
                    id='0', 
                    mkstream=True
                )
            )
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                logger.error(f"Error creating consumer group: {e}")

    async def consume_stream_messages(self):
        """Consume messages from Redis Streams"""
        while True:
            try:
                # Read from stream
                messages = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.redis_client.xreadgroup(
                        self.consumer_group,
                        self.consumer_name,
                        {self.stream_key: '>'},
                        count=1,
                        block=1000  # Block for 1 second
                    )
                )
                
                for stream, msgs in messages:
                    for msg_id, fields in msgs:
                        await self.process_stream_message(msg_id, fields)
                        
            except Exception as e:
                logger.error(f"Error consuming stream messages: {e}")
                await asyncio.sleep(1)

    async def process_stream_message(self, msg_id, fields):
        """Process a message from Redis Streams"""
        try:
            # Skip messages from this consumer to avoid duplicates
            if fields.get('consumer_name') == self.consumer_name:
                # Acknowledge the message
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.redis_client.xack(self.stream_key, self.consumer_group, msg_id)
                )
                return

            # Process the message
            message_data = json.loads(fields.get('data', '{}'))
            await self.send(text_data=json.dumps(message_data))
            
            # Acknowledge the message
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.redis_client.xack(self.stream_key, self.consumer_group, msg_id)
            )
            
        except Exception as e:
            logger.error(f"Error processing stream message: {e}")

    async def disconnect(self, close_code):
        """
        Leave the room group on disconnect and cleanup Redis Streams.
        """
        # Remove from consumer group
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.redis_client.xgroup_delconsumer(
                    self.stream_key,
                    self.consumer_group,
                    self.consumer_name
                )
            )
        except Exception as e:
            logger.error(f"Error removing consumer: {e}")

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
            await self.handle_delete_message(data.get('messageId'))
        elif message_type == 'update':
            await self.handle_update_message(
                data.get('messageId'),
                data.get('message')
            )

    async def publish_to_stream(self, message_data):
        """Publish message to Redis Streams"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.redis_client.xadd(
                    self.stream_key,
                    {
                        'data': json.dumps(message_data),
                        'consumer_name': self.consumer_name,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                )
            )
        except Exception as e:
            logger.error(f"Error publishing to stream: {e}")

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
        message_data = {
            'type': 'chat_message',
            'action': 'new',
            **serialized,
        }

        # Publish to both channels and Redis Streams
        await self.channel_layer.group_send(self.room_group_name, message_data)
        await self.publish_to_stream(message_data)

    async def handle_delete_message(self, message_id):
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
        message_data = {
            'type': 'chat_message',
            'action': 'delete',
            'id': message_id,
        }

        # Publish to both channels and Redis Streams
        await self.channel_layer.group_send(self.room_group_name, message_data)
        await self.publish_to_stream(message_data)

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

        message_data = {
            'type': 'chat_message',
            'action': 'update',
            'id': message_id,
            'body': new_body,
            'edited': True,
            'updated': updated_ts.isoformat() if updated_ts else None,
        }

        # Publish to both channels and Redis Streams
        await self.channel_layer.group_send(self.room_group_name, message_data)
        await self.publish_to_stream(message_data)

    async def chat_message(self, event):
        """
        Receive messages sent to the group and relay to WebSocket clients.
        """
        await self.send(text_data=json.dumps(event))

    async def get_message_history(self, start_id='0', count=50):
        """Retrieve message history from Redis Streams"""
        try:
            messages = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.redis_client.xrange(
                    self.stream_key,
                    start_id,
                    '+',
                    count=count
                )
            )
            
            history = []
            for msg_id, fields in messages:
                try:
                    message_data = json.loads(fields.get('data', '{}'))
                    history.append({
                        'id': msg_id,
                        'timestamp': fields.get('timestamp'),
                        **message_data
                    })
                except json.JSONDecodeError:
                    continue
                    
            return history
        except Exception as e:
            logger.error(f"Error retrieving message history: {e}")
            return []
