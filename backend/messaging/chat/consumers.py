import json
import logging
import uuid
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.utils.timezone import now
from redis.exceptions import RedisError

from backend.core.apps import CoreConfig
from backend.core.exceptions import (
    DomainException,
    FormValidationException,
)

if TYPE_CHECKING:
    from datetime import datetime

logger = logging.getLogger(__name__)


class ClientMessageType(StrEnum):
    TEXT = "text"
    DELETE = "delete"
    UPDATE = "update"
    MARK_SEEN = "mark_seen"


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream_key: str | None = None
        self.initialized: bool = False
        self.room_id: uuid.UUID | None = None
        self.room = None
        self._last_seen_updated_at: datetime | None = None

    @property
    def redis_client(self):
        """Shared Redis client — one connection pool for all consumers."""
        return CoreConfig.get_redis_client()

    @property
    def max_messages_per_second(self) -> int:
        """Set `MAX_MESSAGES_PER_SEC=0` to disable rate limiting."""
        from django.conf import settings

        return settings.MAX_MESSAGES_PER_SEC

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _parse_message_type(self, raw: Any) -> ClientMessageType | None:
        if raw is None:
            return ClientMessageType.TEXT
        try:
            return ClientMessageType(str(raw))
        except ValueError:
            return None

    def _parse_uuid(self, value: Any) -> uuid.UUID | None:
        try:
            return uuid.UUID(str(value))
        except (ValueError, AttributeError):
            return None

    async def _rate_limited(self) -> bool:
        limit = self.max_messages_per_second
        if limit <= 0:
            return False

        if not self.room_id or not self.user:
            return False

        key = f"ws_rl:{self.room_id}:{self.user.id}"
        try:
            pipe = self.redis_client.pipeline(transaction=True)
            pipe.incr(key)
            pipe.expire(key, 1)
            count, _ = await pipe.execute()
            return count > limit
        except (RedisError, OSError):
            logger.warning("Rate limit check failed (redis unavailable)", exc_info=True)
            return False

    async def _maybe_update_last_seen(self) -> None:
        from backend.account.utils import get_inactivity_threshold, update_last_seen

        threshold = get_inactivity_threshold()
        if (
            self._last_seen_updated_at is None
            or (now() - self._last_seen_updated_at) > threshold
        ):
            await database_sync_to_async(update_last_seen)(user=self.user)
            self._last_seen_updated_at = now()

    # TODO: standardize error message format
    async def send_error(self, error_message):
        """
        Send an error message to the WebSocket client.
        Accepts a string or a structured dict.
        """
        payload = {"error": error_message}
        await self.send(text_data=json.dumps(payload))

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

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

        raw_room_id = self.scope.get("url_route", {}).get("kwargs", {}).get("room_id")
        try:
            self.room_id = uuid.UUID(str(raw_room_id))
        except (ValueError, TypeError, AttributeError):
            logger.warning(f"Invalid room_id (not a UUID): {raw_room_id!r}")
            await self.close()
            return

        room_id_str = str(self.room_id)
        self.room_group_name = f"chat_{room_id_str}"
        self.stream_key = f"chat_stream:{room_id_str}"

        from backend.access.models import Participant
        from backend.room.models import Room

        room = await database_sync_to_async(
            Room.objects.filter(id=self.room_id).first
        )()
        if room is None:
            logger.warning(f"Room not found: {self.room_id}")
            await self.close()
            return

        is_participant = await database_sync_to_async(
            Participant.objects.filter(user=self.user, room=room).exists
        )()
        if not is_participant:
            await self.close()
            return

        # Cache room to avoid DB lookup on every received message
        self.room = room

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        self.initialized = True
        await self.accept()

        @database_sync_to_async
        def backfill_delivered():
            from backend.messaging.models import Message
            from backend.messaging.services import MessageStatusService

            limit = settings.DELIVERED_BACKFILL_LIMIT

            msg_ids = list(
                Message.objects.filter(room=self.room)
                .order_by("-created_at")[:limit]
                .values_list("id", flat=True)
            )
            if msg_ids:
                MessageStatusService.mark_delivered(
                    user=self.user, room=self.room, message_ids=msg_ids
                )

        await backfill_delivered()

    async def disconnect(self, close_code):
        """Leave the room group on disconnect."""
        if not self.initialized:
            return

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # Do NOT close the shared Redis client here.

    # ------------------------------------------------------------------
    # Message routing
    # ------------------------------------------------------------------

    async def receive(self, text_data):
        """
        Handle incoming messages: text, delete, or update.
        Assumes only participants reach this point.
        """
        if await self._rate_limited():
            await self.send_error("Too many messages. Please slow down.")
            return

        await self._maybe_update_last_seen()

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
            parent_id = self._parse_uuid(data.get("parentId"))
            await self.handle_new_message(room, message_body, parent_id=parent_id)
            return

        if msg_type is ClientMessageType.DELETE:
            message_id = self._parse_uuid(data.get("messageId"))
            if not message_id:
                await self.send_error("Invalid or missing 'messageId'.")
                return
            await self.handle_delete_message(message_id)
            return

        if msg_type is ClientMessageType.UPDATE:
            message_id = self._parse_uuid(data.get("messageId"))
            new_body = data.get("message")
            if not message_id:
                await self.send_error("Invalid or missing 'messageId'.")
                return
            if not isinstance(new_body, str):
                await self.send_error("Missing or invalid 'message'.")
                return
            await self.handle_update_message(message_id, new_body)
            return

        if msg_type is ClientMessageType.MARK_SEEN:
            raw_ids = data.get("messageIds")
            if not isinstance(raw_ids, list):
                await self.send_error("Missing or invalid 'messageIds'.")
                return
            message_ids = [self._parse_uuid(mid) for mid in raw_ids]
            message_ids = [mid for mid in message_ids if mid is not None]
            if not message_ids:
                return
            await self.handle_mark_seen(message_ids)
            return

    # ------------------------------------------------------------------
    # Message handlers
    # ------------------------------------------------------------------

    async def handle_new_message(self, room, message_body, parent_id=None):
        """Handle creation of a new message."""
        from backend.messaging.services import MessageService

        @database_sync_to_async
        def create_message(user, room, body, parent_id):
            return MessageService.create_message(
                user=user, room=room, body=body, parent_id=parent_id
            )

        @database_sync_to_async
        def serialize(message):
            return MessageService.serialize(message)

        try:
            new_message = await create_message(
                user=self.user, room=room, body=message_body, parent_id=parent_id
            )
        except FormValidationException as e:
            await self.send_error({"message": str(e), "errors": e.errors})
            return
        except DomainException as e:
            await self.send_error(str(e))
            return

        serialized = await serialize(new_message)
        message_data = {
            "type": "chat_message",
            "action": "new",
            **serialized,
        }

        await self.channel_layer.group_send(self.room_group_name, message_data)
        await self.publish_to_stream(message_data)

    async def handle_delete_message(self, message_id: uuid.UUID):
        """Handle deletion of a message."""
        from backend.messaging.models import Message
        from backend.messaging.services import MessageService

        @database_sync_to_async
        def get_message():
            return Message.objects.filter(id=message_id).first()

        @database_sync_to_async
        def delete_message(message):
            return MessageService.delete_message(self.user, message)

        message = await get_message()
        if message is None:
            await self.send_error("Message not found.")
            return

        try:
            await delete_message(message)
        except DomainException as e:
            await self.send_error(str(e))
            return

        message_data = {
            "type": "chat_message",
            "action": "delete",
            "id": str(message_id),
        }

        await self.channel_layer.group_send(self.room_group_name, message_data)
        await self.publish_to_stream(message_data)

    async def handle_update_message(self, message_id: uuid.UUID, new_body: str):
        """Handle updating a message."""
        from backend.messaging.models import Message
        from backend.messaging.services import MessageService

        @database_sync_to_async
        def get_message():
            return Message.objects.filter(id=message_id).first()

        @database_sync_to_async
        def do_update(message):
            return MessageService.update_message(
                user=self.user, message=message, body=new_body
            )

        @database_sync_to_async
        def serialize(message):
            return MessageService.serialize(message)

        message = await get_message()
        if message is None:
            await self.send_error("Message not found.")
            return

        try:
            updated_message = await do_update(message)
        except FormValidationException as e:
            await self.send_error({"message": str(e), "errors": e.errors})
            return
        except DomainException as e:
            await self.send_error(str(e))
            return

        serialized = await serialize(updated_message)
        message_data = {
            "type": "chat_message",
            "action": "update",
            **serialized,
        }

        await self.channel_layer.group_send(self.room_group_name, message_data)
        await self.publish_to_stream(message_data)

    async def handle_mark_seen(self, message_ids: list[uuid.UUID]):
        """Handle marking messages as seen by the current user."""
        from backend.messaging.services import MessageStatusService

        room = self.room

        @database_sync_to_async
        def mark_seen(user, ids):
            return MessageStatusService.mark_seen(user=user, room=room, message_ids=ids)

        try:
            updates = await mark_seen(self.user, message_ids)
        except Exception:
            logger.error("Failed to mark messages as seen", exc_info=True)
            return

        if not updates:
            return

        status_data = {
            "type": "chat_message",
            "action": "status_update",
            "updates": updates,
        }

        await self.channel_layer.group_send(self.room_group_name, status_data)

    async def chat_message(self, event):
        """Receive messages broadcast to the group and relay to this client."""
        if event.get("action") == "new":
            msg_id = self._parse_uuid(event.get("id"))
            author_id = event.get("author_id")
            if msg_id and str(self.user.id) != str(author_id):
                from backend.messaging.choices import MessageStatusChoices

                @database_sync_to_async
                def mark_delivered():
                    from backend.messaging.services import MessageStatusService

                    return MessageStatusService.mark_delivered(
                        user=self.user, room=self.room, message_ids=[msg_id]
                    )

                try:
                    # Non-empty only when rows were actually inserted (ON CONFLICT DO NOTHING)
                    created = await mark_delivered()
                except Exception:
                    logger.error("Failed to mark message as delivered", exc_info=True)
                    created = []

                if created:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "chat_message",
                            "action": "status_update",
                            "updates": [
                                {
                                    "message_id": str(msg_id),
                                    "user_id": str(self.user.id),
                                    "status": MessageStatusChoices.DELIVERED,
                                }
                            ],
                        },
                    )

        await self.send(text_data=json.dumps(event))

    async def publish_to_stream(self, message_data):
        """Publish a message to Redis Streams for history/persistence."""
        try:
            await self.redis_client.xadd(
                self.stream_key,
                {
                    "data": json.dumps(message_data),
                    "timestamp": now().isoformat(),
                },
            )
        except TypeError:
            logger.error("Message data not JSON-serializable", exc_info=True)
        except (RedisError, OSError):
            logger.error(
                "Error publishing to stream (redis unavailable)", exc_info=True
            )

    async def get_message_history(self, start_id="0", count=50):
        """Retrieve message history from Redis Streams."""
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
                logger.warning(
                    f"Corrupt JSON in redis stream entry {msg_id}", exc_info=True
                )
                continue

            history.append(
                {"id": msg_id, "timestamp": fields.get("timestamp"), **message_data}
            )
        return history
