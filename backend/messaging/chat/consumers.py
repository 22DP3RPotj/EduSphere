import json
import logging
from datetime import datetime
from enum import StrEnum
from typing import Any, Optional

import redis.asyncio as aioredis
from redis.exceptions import RedisError
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)


class ClientMessageType(StrEnum):
    TEXT = "text"
    DELETE = "delete"
    UPDATE = "update"


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Async Redis client (avoids per-call thread executor overhead)
        self.redis_client = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        self.stream_key = None
        self.initialized = False
        self.room_id = None
        self.room = None

    # TODO: Move validation to forms
    @property
    def max_body_length(self):
        """
        Return the maximum length of the message body.
        """
        from backend.messaging.models import Message

        return Message._meta.get_field("body").max_length

    @property
    def max_messages_per_second(self) -> int:
        """Set `MAX_MESSAGES_PER_SEC=0` to disable."""
        return settings.MAX_MESSAGES_PER_SEC

    def _parse_message_type(self, raw: Any) -> Optional[ClientMessageType]:
        if raw is None:
            return ClientMessageType.TEXT
        try:
            return ClientMessageType(str(raw))
        except ValueError:
            return None

    async def _rate_limited(self) -> bool:
        limit = self.max_messages_per_second
        if limit <= 0:
            return False

        if not self.room_id or not self.user:
            return False

        key = f"ws_rl:{self.room_id}:{self.user.id}"
        try:
            count = await self.redis_client.incr(key)
            if count == 1:
                await self.redis_client.expire(key, 1)
            return count > limit
        except (RedisError, OSError):
            # If Redis is down, fail open rather than breaking chat entirely.
            logger.warning("Rate limit check failed (redis unavailable)", exc_info=True)
            return False

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
        user = self.scope.get("user")

        if not user or not user.is_authenticated:
            await self.close()
            return

        self.user = user
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        room_id_str = str(self.room_id)
        self.room_group_name = f"chat_{room_id_str}"

        # Redis Streams history key
        self.stream_key = f"chat_stream:{room_id_str}"

        from backend.room.models import Room
        from backend.access.models import Participant

        try:
            room = await database_sync_to_async(Room.objects.get)(id=self.room_id)
        except Room.DoesNotExist:
            logger.warning(f"Room not found: {self.room_id}")
            await self.close()
            return

        is_participant = await database_sync_to_async(
            Participant.objects.filter(user=self.user, room=room).exists
        )()

        if not is_participant:
            logger.warning(
                f"User {self.user.username} ({self.user.id}) is not a participant of room {room.id}"
            )
            await self.close()
            return

        # Cache room to avoid DB lookup on every received message
        self.room = room

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        self.initialized = True
        await self.accept()

    async def disconnect(self, close_code):
        """
        Leave the room group on disconnect.
        """
        if not self.initialized:
            return

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        try:
            await self.redis_client.aclose()
        except (RedisError, OSError):
            logger.warning("Error closing redis client.", exc_info=True)

    async def receive(self, text_data):
        """
        Handle incoming messages: text, delete, or update.
        Assumes only participants reach this point.
        """
        if await self._rate_limited():
            await self.send_error("Too many messages. Please slow down.")
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON.")
            return

        msg_type = self._parse_message_type(data.get("type"))
        if msg_type is None:
            await self.send_error("Unknown message type.")
            return

        # `self.room` is cached in connect(); fall back defensively.
        room = self.room
        if room is None:
            await self.send_error("Room not loaded.")
            return

        if msg_type is ClientMessageType.TEXT:
            message_body = data.get("message")
            if not isinstance(message_body, str):
                await self.send_error("Missing or invalid 'message'.")
                return
            # TODO: move to form validation
            if len(message_body) > self.max_body_length:
                await self.send_error(
                    f"Message exceeds {self.max_body_length} characters."
                )
                return
            await self.handle_new_message(room, message_body)
            return

        if msg_type is ClientMessageType.DELETE:
            message_id = data.get("messageId")
            if not message_id:
                await self.send_error("Missing 'messageId'.")
                return
            await self.handle_delete_message(message_id)
            return

        if msg_type is ClientMessageType.UPDATE:
            message_id = data.get("messageId")
            new_body = data.get("message")
            if not message_id:
                await self.send_error("Missing 'messageId'.")
                return
            if not isinstance(new_body, str):
                await self.send_error("Missing or invalid 'message'.")
                return
            if len(new_body) > self.max_body_length:
                await self.send_error(
                    f"Message exceeds {self.max_body_length} characters."
                )
                return
            await self.handle_update_message(message_id, new_body)
            return

    async def publish_to_stream(self, message_data):
        """Publish message to Redis Streams (history/persistence only)."""
        try:
            await self.redis_client.xadd(
                self.stream_key,
                {
                    "data": json.dumps(message_data),
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except TypeError:
            logger.error("Message data not JSON-serializable", exc_info=True)
        except (RedisError, OSError):
            logger.error(
                "Error publishing to stream (redis unavailable)", exc_info=True
            )

    async def handle_new_message(self, room, message_body):
        """Handle creation of a new message"""
        from backend.messaging.models import Message
        from backend.messaging.services import MessageService

        @database_sync_to_async
        def create_message(user, room, body):
            message = Message(user=user, room=room, body=body)
            message.full_clean()
            message.save()
            return message

        @database_sync_to_async
        def serialize(message):
            return MessageService.serialize(message)

        try:
            new_message = await create_message(
                user=self.user, room=room, body=message_body
            )
        except ValidationError:
            await self.send_error(f"Message exceeds {self.max_body_length} characters.")
            return

        serialized = await serialize(new_message)
        message_data = {
            "type": "chat_message",
            "action": "new",
            **serialized,
        }

        # Realtime fanout (single mechanism)
        await self.channel_layer.group_send(self.room_group_name, message_data)
        await self.publish_to_stream(message_data)

    async def handle_delete_message(self, message_id):
        """Handle deletion of a message"""
        from backend.messaging.models import Message
        from backend.messaging.services import MessageService
        from backend.core.exceptions import PermissionException

        @database_sync_to_async
        def get_message():
            return Message.objects.get(id=message_id)

        @database_sync_to_async
        def delete_with_service(message):
            return MessageService.delete_message(self.user, message)

        try:
            message = await get_message()
        except Message.DoesNotExist:
            await self.send_error("Message not found.")
            return

        try:
            await delete_with_service(message)
        except PermissionException as e:
            await self.send_error(str(e))
            return

        message_data = {
            "type": "chat_message",
            "action": "delete",
            "id": message_id,
        }

        # Realtime fanout (single mechanism)
        await self.channel_layer.group_send(self.room_group_name, message_data)
        await self.publish_to_stream(message_data)

    async def handle_update_message(self, message_id, new_body):
        """Handle updating a message"""
        from backend.messaging.models import Message
        from backend.messaging.services import MessageService

        @database_sync_to_async
        def get_message():
            return Message.objects.get(id=message_id)

        @database_sync_to_async
        def check_owner(message):
            return message.user_id == self.user.id

        @database_sync_to_async
        def do_update(message):
            message = MessageService.update_message(
                user=self.user, message=message, body=new_body
            )
            return message.updated_at

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
            await self.send_error(f"Message exceeds {self.max_body_length} characters.")
            return

        message_data = {
            "type": "chat_message",
            "action": "update",
            "id": message_id,
            "body": new_body,
            "is_edited": True,
            "updated_at": updated_ts.isoformat() if updated_ts else None,
        }

        # Realtime fanout (single mechanism)
        await self.channel_layer.group_send(self.room_group_name, message_data)
        await self.publish_to_stream(message_data)

    async def chat_message(self, event):
        """
        Receive messages sent to the group and relay to WebSocket clients.
        """
        await self.send(text_data=json.dumps(event))

    async def get_message_history(self, start_id="0", count=50):
        """Retrieve message history from Redis Streams"""
        try:
            messages = await self.redis_client.xrange(
                self.stream_key, start_id, "+", count=count
            )
        except (RedisError, OSError):
            logger.error(
                "Error retrieving message history (redis unavailable).", exc_info=True
            )
            return []

        history = []
        for msg_id, fields in messages:
            raw = fields.get("data")
            if not raw:
                continue
            try:
                message_data = json.loads(raw)
            except json.JSONDecodeError:
                # Corrupt entry in stream: skip but keep going
                logger.warning(
                    f"Corrupt JSON in redis stream entry {msg_id}", exc_info=True
                )
                continue

            history.append(
                {"id": msg_id, "timestamp": fields.get("timestamp"), **message_data}
            )
        return history
